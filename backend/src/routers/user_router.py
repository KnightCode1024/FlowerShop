from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request, status

from core.rate_limiter import RateLimiter, Strategy, rate_limit
from schemas.user import (AccessToken, OTPCode, RefreshToken, TokenPair,
                          UserCreate, UserLogin, UserResponse, UserUpdate)
from services import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    route_class=DishkaRoute,
)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    service: FromDishka[UserService],
):
    try:
        return await service.register_user(user_data)
    except ValueError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


@router.get("/verify-email")
async def verify_email(
    token: str,
    service: FromDishka[UserService],
):
    try:
        return await service.verify_email(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/check-code", response_model=TokenPair)
async def check_code(
    code: OTPCode,
    service: FromDishka[UserService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.check_code(current_user, code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/resend-otp")
async def resend_otp(
    service: FromDishka[UserService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.resend_otp_code(current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=AccessToken)
async def login(
    user_data: UserLogin,
    service: FromDishka[UserService],
):
    try:
        return await service.login_user(user_data)
    except ValueError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e}",
        )


@router.get("/me", response_model=UserResponse)
# @rate_limit(strategy=Strategy.USER, policy="3/s;10/m;100/h")
async def get_profile(
    request: Request,
    rate_limiter: FromDishka[RateLimiter],
    current_user: FromDishka[UserResponse],
):
    return current_user


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    payload: RefreshToken,
    service: FromDishka[UserService],
):
    try:
        return await service.refresh_token(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    service: FromDishka[UserService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.update_user(
            current_user.id,
            user_data,
            current_user,
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    service: FromDishka[UserService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.get_all_users(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    service: FromDishka[UserService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.get_user(user_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e}",
        )
