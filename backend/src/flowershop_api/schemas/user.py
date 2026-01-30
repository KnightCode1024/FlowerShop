import re

from pydantic import BaseModel, field_validator, Field

from flowershop_api.models import RoleEnum


class UserEmail(BaseModel):
    email: str = Field(..., max_length=255)

    @field_validator("email", mode="after")
    @classmethod
    def is_valid_email(cls, value: int) -> int:
        email_validate_pattern = r"^\S+@\S+\.\S+$"
        if not re.match(email_validate_pattern, value):
            raise ValueError(f"{value} is not correct email")
        return value


class UserBase(UserEmail):
    username: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class UserCreate(UserBase):
    pass


class UserCreateConsole(UserBase):
    role: RoleEnum

    @field_validator("role", mode="after")
    @classmethod
    def validate_role_for_console(cls, value: str) -> str:
        valid_roles = [RoleEnum.USER, RoleEnum.EMPLOYEE, RoleEnum.ADMIN]
        if value not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return value


class UserLogin(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class UserUpdate(UserBase):
    pass


class UserRequest(BaseModel):
    id: int = Field(...)


class UserResponse(UserEmail):
    id: int = Field(...)
    username: str = Field(..., max_length=255)
    role: RoleEnum | str = Field(..., max_length=255)


class AnonymousUserResponse(BaseModel):
    id: int | None = Field(None)
    username: str | None = Field(None, max_length=255)
    role: RoleEnum = Field(default=RoleEnum.ANONYMOUS, max_length=255)
    email: str | None = Field(None, max_length=255)

    class Config:
        pass


class RefreshToken(BaseModel):
    refresh_token: str = Field(...)


class TokenPair(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
