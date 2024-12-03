# import socketio

# from backend.core.conf import settings
# from backend.common.security.jwt import jwt_authentication
# from backend.common.log import log

# sio = socketio.AsyncServer(
#     client_manager=socketio.AsyncRedisManager(
#         f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:'
#         f'{settings.REDIS_PORT}/{task_settings.CELERY_BROKER_REDIS_DATABASE}'
#     )
#     if task_settings.CELERY_BROKER == 'redis'
#     else socketio.AsyncAioPikaManager(
#         (
#             f'amqp://{task_settings.RABBITMQ_USERNAME}:{task_settings.RABBITMQ_PASSWORD}@'
#             f'{task_settings.RABBITMQ_HOST}:{task_settings.RABBITMQ_PORT}'
#         )
#     ),
#     async_mode='asgi',
#     cors_allowed_origins=settings.CORS_ALLOWED_ORIGINS,
#     cors_credentials=True,
#     namespaces=['/ws'],
# )

# @sio.event
# async def connect(sid, environ, auth):
#     if not auth:
#         print('ws connection failed: no authorization')
#         return False

#     token = auth.get('token')
#     if not token:
#         print('ws connection failed: no token authorization')
#         return False

#     if token == 'internal':
#         return True

#     try:
#         await jwt_authentication(token)
#     except Exception as e:
#         log.info(f'ws Connection failed: {e}')
#         return False

#     return True


# @sio.event
# async def disconnect(sid):
#     pass