from dishka import Provider, Scope, provide
from fastapi import HTTPException, Request, status
from jwt import InvalidTokenError

from flowershop_api.schemas.user import UserResponse
from flowershop_api.services.user import UserService
from flowershop_api.utils.jwt_utils import decode_jwt


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_current_user(
        self,
        user_service: UserService,
        request: Request,
    ) -> UserResponse:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        try:
            decoded_token = decode_jwt(token)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user_id = int(decoded_token.get("sub"))

        if user_id:
            user = await user_service.get_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
            )
