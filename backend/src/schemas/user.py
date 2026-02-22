import re

from pydantic import BaseModel, Field, field_validator

from models import RoleEnum


class UserEmail(BaseModel):
    email: str = Field(..., max_length=255)

    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, value) -> str:
        email_validate_pattern = r"^\S+@\S+\.\S+$"
        if not re.match(email_validate_pattern, value):
            raise ValueError(f"{value} is not correct email")
        return value


class UserBase(UserEmail):
    username: str = Field(..., max_length=30)
    password: str = Field(..., max_length=255)


class UserCreate(UserBase):
    pass


class UserCreateConsole(UserBase):
    role: RoleEnum


class UserLogin(UserEmail):
    # email: str = Field(..., max_length=64)
    password: str = Field(..., max_length=255)


class UserUpdate(BaseModel):
    username: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=255)
    password: str | None = Field(None, max_length=255)


class UserRequest(BaseModel):
    id: int = Field(...)


class UserResponse(UserEmail):
    id: int = Field(...)
    username: str = Field(..., max_length=30)
    # email_verified: bool = Field(...)
    role: RoleEnum | str = Field(..., max_length=10)


class RefreshToken(BaseModel):
    refresh_token: str = Field(...)


class TokenPair(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)


class OTPCode(BaseModel):
    otp_code: str


class AccessToken(BaseModel):
    access_token: str = Field(...)
