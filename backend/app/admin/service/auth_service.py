from fastapi import Request, Response
from fastapi.security import HTTPBasicCredentials
from datetime import datetime
from starlette.background import BackgroundTask, BackgroundTasks

from backend.crud.crud_user import user_dao
from backend.models.user import User
from backend.schemas.token import GetLoginToken, GetNewToken
from backend.app.admin.schema.user import UserLoginSchema, UserRegister
from backend.app.admin.service.login_log_service import LoginLogService
from backend.common.enums import LoginLogStatusType
from backend.common.exception import errors
from backend.common.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_token,
    jwt_decode,
    password_verify,
)
from backend.core.conf import settings
from backend.database.db_postgres import async_db_session
from backend.database.db_redis import redis_client
from backend.utils.timezone import timezone
from backend.utils.translator import Translator


class AuthService:
    @staticmethod
    async def swagger_login(*, obj: HTTPBasicCredentials) -> tuple[str, User]:
        async with async_db_session.begin() as db:
            current_user = await user_dao.get_by_email(db, obj.username)
            if not current_user:
                raise errors.NotFoundError(msg='Incorrect email or password')
            elif not password_verify(f'{obj.password}{current_user.salt}', current_user.password):
                raise errors.AuthorizationError(msg='Incorrect email or password')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='The user has been locked out. Please contact the system useristrator.')
            access_token = await create_access_token(str(current_user.x_id), False)
            await user_dao.update_login_time(db, obj.username)
            return access_token.access_token, current_user

    @staticmethod
    async def register(
        *, request: Request, response: Response, obj: UserRegister, background_tasks: BackgroundTasks
        ) -> GetLoginToken:
        translator = Translator(request.state.locale)

        async with async_db_session.begin() as db:
            if not obj.password:
                raise errors.ForbiddenError(msg=translator.t('auth.enpty_password'))
            
            email = await user_dao.get_by_email(db, obj.email)
            if email:
                raise errors.ForbiddenError(msg=translator.t('auth.exist'))
            
            new_user = await user_dao.add(db, obj)

            # current_user_id = new_user.x_id
            # is_multi_login = new_user.is_multi_login
            user_x_id = new_user.x_id
            email = new_user.email
            
            access_token = await create_access_token(str(user_x_id), False)
            refresh_token = await create_refresh_token(str(user_x_id), False)

            n_user = await user_dao.get_with_relation(db, x_id=user_x_id, populates=['roles'])
        
            background_tasks.add_task(
                LoginLogService.create,
                **dict(
                    db=db,
                    request=request,
                    user_x_id=user_x_id,
                    email=email,
                    login_time=datetime.now(),
                    status=LoginLogStatusType.success.value,
                    msg=translator.t('auth.successful'),
                )
            )

            # await user_dao.update_login_time(db, obj.email)
            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY,
                value=refresh_token.refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                httponly=True,
                samesite='none'
            )
            
            data = GetLoginToken(
                access_token=access_token.access_token,
                access_token_expire_time=access_token.access_token_expire_time,
                user=n_user,  # type: ignore
            )
            return data


    @staticmethod
    async def login(
        *, request: Request, response: Response, obj: UserLoginSchema, background_tasks: BackgroundTasks
    ) -> GetLoginToken:
        translator = Translator(request.state.locale)

        async with async_db_session.begin() as db:
            try:
                current_user = await user_dao.get_by_email(db, email=obj.email, populates=['roles'])
                if not current_user:
                    raise errors.NotFoundError(msg=translator.t('auth.incorrect_credential'))

                user_x_id = current_user.x_id
                email = current_user.email

                if not password_verify(obj.password + current_user.salt, current_user.password):
                    raise errors.AuthorizationError(msg=translator.t('auth.incorrect_credential'))
                elif not current_user.status:
                    raise errors.AuthorizationError(msg=translator.t('auth.account_locked'))

                access_token = await create_access_token(str(user_x_id), False)
                refresh_token = await create_refresh_token(str(user_x_id), False)

            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg)
            except (errors.AuthorizationError, errors.CustomError) as e:
                task = BackgroundTask(
                    LoginLogService.create,
                    **dict(
                        db=db,
                        request=request,
                        user_x_id=user_x_id,
                        email=email,
                        login_time=datetime.now(),
                        status=LoginLogStatusType.fail.value,
                        msg=e.msg,
                    ),
                )
                raise errors.AuthorizationError(msg=e.msg, background=task)
            except Exception as e:
                raise e
            else:
                background_tasks.add_task(
                    LoginLogService.create,
                    **dict(
                        db=db,
                        request=request,
                        user_x_id=user_x_id,
                        email=email,
                        login_time=datetime.now(),
                        status=LoginLogStatusType.success.value,
                        msg=translator.t('auth.successful'),
                    ),
                )
                # await redis_client.delete(f'{user_settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')

                await user_dao.update_login_time(db, obj.email)
                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                    httponly=True,
                    samesite='none'
                )
                await db.refresh(current_user)
                data = GetLoginToken(
                    access_token=access_token.access_token,
                    access_token_expire_time=access_token.access_token_expire_time,
                    user=current_user,  # type: ignore
                )
                return data


    @staticmethod
    async def new_token(*, request: Request, response: Response) -> GetNewToken:
        translator = Translator(request.state.locale)
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)

        if not refresh_token:
            raise errors.TokenError(msg=translator.t('auth.refresh_token_not_found'))
        try:
            user_x_id = jwt_decode(refresh_token)
        except Exception:
            raise errors.TokenError(msg=translator.t('auth.invalid_refresh_token'))
        # if request.user.id != user_id:
        #     raise errors.TokenError(msg='Refresh Token is invalid')
        async with async_db_session() as db:
            current_user = await user_dao.get_by_x_id(db, user_x_id)
            if not current_user:
                raise errors.NotFoundError(msg=translator.t('auth.incorrect_credential'))
            elif not current_user.status:
                raise errors.AuthorizationError(msg=translator.t('auth.account_locked'))
            current_token = get_token(request)
            new_token = await create_new_token(
                sub=str(current_user.x_id),
                token=current_token,
                refresh_token=refresh_token,
                multi_login=False,
            )
            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY,
                value=new_token.new_refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=timezone.f_utc(new_token.new_refresh_token_expire_time),
                httponly=True,
                samesite='none'
            )
            data = GetNewToken(
                access_token=new_token.new_access_token,
                access_token_expire_time=new_token.new_access_token_expire_time,
            )
            return data


    @staticmethod
    async def logout(*, request: Request, response: Response) -> None:
        token = get_token(request)
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)
        # if request.user.is_multi_login:
        #     key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}'
        #     await redis_client.delete(key)
        #     if refresh_token:
        #         key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:{refresh_token}'
        #         await redis_client.delete(key)
        # else:
        key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.x_id}:'
        await redis_client.delete_prefix(key_prefix)
        key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.x_id}:'
        await redis_client.delete_prefix(key_prefix)


auth_service = AuthService()
