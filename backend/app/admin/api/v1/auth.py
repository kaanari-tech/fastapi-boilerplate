from fastapi import APIRouter, Request, Response
from starlette.background import BackgroundTasks

from backend.app.admin.schema.user import (
    GetCurrentUserInfoDetail,
    # UpdatePasswordParam,
    UserLoginSchema,
    UserRegister
)
from backend.app.admin.service.auth_service import auth_service
# from backend.app.user.service.user_service import user_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth

router = APIRouter(prefix="/auth", tags=["User Auth"])


@router.post('/register', summary='registered user')
async def register_user(request: Request, response: Response, obj: UserRegister, background_tasks: BackgroundTasks) -> ResponseModel:
    data = await auth_service.register(request=request, response=response, obj=obj, background_tasks=background_tasks)
    
    return response_base.success(request=request, data=data)


@router.post(
    '/login',
    summary='user login',
    description='json format, only supports debugging in third-party api tools, e.g. postman.',
    # dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
async def user_login(
    request: Request, response: Response, obj: UserLoginSchema, background_tasks: BackgroundTasks
) -> ResponseModel:
    data = await auth_service.login(request=request, response=response, obj=obj, background_tasks=background_tasks)
    return response_base.success(request=request, data=data)


@router.post('/token/new', summary='Create a new token', dependencies=[DependsJwtAuth])
async def create_new_token(request: Request, response: Response) -> ResponseModel:
    data = await auth_service.new_token(request=request, response=response)
    return response_base.success(request=request, data=data)


@router.post('/logout', summary='user logout', dependencies=[DependsJwtAuth])
async def user_logout(request: Request, response: Response) -> ResponseModel:
    await auth_service.logout(request=request, response=response)
    return response_base.success(request=request)


@router.get('/me', summary='Get connected user profile', dependencies=[DependsJwtAuth], response_model_exclude={'password'})
async def get_current_user(request: Request) -> ResponseModel:
    data = GetCurrentUserInfoDetail(**request.user.model_dump())
    return response_base.success(request=request, data=data)






