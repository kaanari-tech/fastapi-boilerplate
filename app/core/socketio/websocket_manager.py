from typing import Any

import socketio
from fastapi.encoders import jsonable_encoder
from schemas import NotificationCreate

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

    # verify if user realy exist
    user = crud.user_sync.get_db_obj_by_id(db=next(get_db()), id=user_id)
    if not user:
        await sio.disconnect(sid=sid, ignore_queue=True)
        return

    # add user to all connected user
    CONNECTION.append({"user_id": str(user.id), "sid": sid})

    # add user to room
    enter_room(sid=sid, room_name=str(user.id))

    # save user data in a session
    await sio.save_session(sid=sid, session=user)
    print("--> CONNECTED ")


@sio.event
async def disconnect(sid):
    # get user data from the session
    connected_user = await sio.get_session(sid=sid)

    # leave user from room
    leave_room(sid=sid, room_name=str(connected_user.id))

    # remove user connection
    for conn in CONNECTION:
        if conn["user_id"] == str(connected_user.id):
            CONNECTION.remove(conn)
    print("--> DISCONNECTED ")


def enter_room(sid: str, room_name: str) -> None:
    sio.enter_room(sid=sid, room=room_name)


def leave_room(sid: str, room_name: str) -> None:
    sio.leave_room(sid=sid, room=room_name)


async def send_personal_notification(data: Any) -> bool:
    # Save notification
    notification = crud.notification_sync.create(
        db=next(get_db()),
        create_schema=NotificationCreate(
            content="Vous avez reçu une nouveaux message...",
            viewed=False,
            type="notification_push",
            user_id=data["message"]["user_id"],
        ),
    )

    # send notification to user
    await sio.emit(
        event="notification",
        data=jsonable_encoder(notification),
        room=data["message"]["user_id"],
    )
    return True
