import json
import logging
from typing import Any
from typing import Dict
from typing import Union

import pika
from asgiref.sync import async_to_sync
from pika.exchange_type import ExchangeType

from app.core.config import settings
from app.core.socketio.websocket_manager import CONNECTION
from app.core.socketio.websocket_manager import send_personal_notification


class MessageQueue:
    def __init__(self) -> None:
        self.host = settings.RABBIT_MQ_HOST
        self.port = settings.RABBIT_MQ_PORT
        self.exchange_name = "notification"
        self.queue_name = "notification_queue"
        self.routing_key = "notfy-x"

        try:
            # Initializing the Message Queue
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port, heartbeat=600)
            )

            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange=self.exchange_name, exchange_type=ExchangeType.fanout
            )
            self.channel.queue_declare(queue=self.queue_name)
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key,
            )
            self.channel.basic_qos(prefetch_count=1)
        except Exception as e:
            logging.error(f"Error connecting to RabbitMQ: {str(e)}")

    async def publish_notification(self, message: Dict[str, Union[int, str]]) -> bool:
        try:
            # Publishing to the queue
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=json.dumps(message),
            )
            return True
        except Exception as e:
            logging.error(f"Error publishing message: {str(e)}")
            return False

    async def consume_messages(self) -> None:
        try:
            logging.info("Messages are now being consumed")

            async def callback_func(
                ch: Any, method: Any, properties: Any, body: Any
            ) -> None:
                if len(CONNECTION) > 0:
                    message_status = await send_personal_notification(json.loads(body))
                    if message_status:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=async_to_sync(callback_func),
                auto_ack=False,
            )
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logging.info("Consumer closed")

    async def fetch_all_messages(self) -> Any:
        try:
            messages = []
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.queue_name
            )
            while method_frame:
                method_frame, header_frame, body = self.channel.basic_get(
                    queue=self.queue_name
                )

                if body:
                    messages.append((method_frame, json.loads(body)))

            return messages

        except Exception as e:
            logging.error(f"Error fetching messages: {str(e)}")
            return None

    async def get_user_messages(self, user_id: int) -> list[dict[str, Any]] | None:
        messages = await self.fetch_all_messages()
        if messages:
            user_messages = [
                {"message": message, "delivery_tag": method_frame.delivery_tag}
                for method_frame, message in messages
                if message["user_id"] == user_id
            ]
            if user_messages:
                return user_messages
        return None

    async def retry_unsent_messages(self, user_id: int) -> bool:
        user_messages = await self.get_user_messages(user_id)
        if user_messages:
            for message in user_messages:
                message_status = await send_personal_notification(message)
                if message_status:
                    self.channel.basic_ack(delivery_tag=message["delivery_tag"])
        return True

    def __del__(self):
        try:
            logging.warning("Closing connection...")
            if self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(f"Error closing connection: {str(e)}")


mq = MessageQueue()
