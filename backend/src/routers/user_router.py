from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request, status

from core.rate_limiter import RateLimiter, Strategy, rate_limit
from schemas.user import (
    AccessToken,
    OTPCode,
    RefreshToken,
    TokenPair,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    )
from services import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    route_class=DishkaRoute,
)


@router.post("/register", response_model=UserResponse)
@rate_limit(strategy=Strategy.IP, policy="3/m;10/h;20/d")
async def register(
    request: Request,
    user_data: UserCreate,
    rate_limiter: FromDishka[RateLimiter],
    service: FromDishka[UserService],
):
    try:
        return await service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


@router.get("/verify-email")
@rate_limit(strategy=Strategy.IP, policy="5/m;20/h")
async def verify_email(
    request: Request,
    token: str,
    rate_limiter: FromDishka[RateLimiter],
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
@rate_limit(strategy=Strategy.IP, policy="5/m;20/h")
async def check_code(
    request: Request,
    code: OTPCode,
    rate_limiter: FromDishka[RateLimiter],
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
@rate_limit(strategy=Strategy.IP, policy="2/m;5/h")
async def resend_otp(
    request: Request,
    rate_limiter: FromDishka[RateLimiter],
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


@rate_limit(strategy=Strategy.IP, policy="5/m;20/h;50/d")
@router.post("/login", response_model=AccessToken)
async def login(
    request: Request,
    user_data: UserLogin,
    rate_limiter: FromDishka[RateLimiter],
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
async def get_profile(
    current_user: FromDishka[UserResponse],
):
    return current_user


@router.post("/refresh", response_model=TokenPair)
@rate_limit(strategy=Strategy.IP, policy="10/m;100/h")
async def refresh_token(
    request: Request,
    payload: RefreshToken,
    rate_limiter: FromDishka[RateLimiter],
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
