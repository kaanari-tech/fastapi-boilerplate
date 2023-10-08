from typing import Any

import socketio

from app import crud
from app.core.config import settings
from app.db.session import get_db

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.BACKEND_CORS_ORIGINS,
    logger=True,
)
asgi_app = socketio.ASGIApp(socketio_server=sio, socketio_path="socket.io")
CONNECTION = []


@sio.event
async def connect(sid, environ, auth):
    user_id = auth.get("USER_ID")
    user = crud.user_sync.get_db_obj_by_id(db=next(get_db()), id=user_id)
    await sio.save_session(sid=sid, session=user)


def enter_room(sid: str, room_name: str) -> None:
    sio.enter_room(sid=sid, room=room_name)


def leave_room(sid: str, room_name: str) -> None:
    sio.leave_room(sid=sid, room=room_name)


async def send_personal_notification(data: Any) -> None:
    await sio.emit(
        # to=str(user_id),
        event="notification",
        data="Notification",
        room=data["message"]["user_id"],
    )
