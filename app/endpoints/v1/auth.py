from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import schemas
from app.core.security import create_token
from app.core.security import get_current_user
from app.db import get_async_db
from app.models import User

router = APIRouter()


@router.post("/login")
async def login(
    db: AsyncSession = Depends(get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect email or password"
        )

    token = create_token({"id": user.id})

    return {
        "access_token": token,
        "token_type": "Bearer",
    }


@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
) -> schemas.UserResponse:
    return current_user
