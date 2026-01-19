import re

from pydantic import BaseModel, field_validator, Field


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


class UserLogin(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class UserUpdate(UserBase):
    pass


class UserResponse(UserEmail):
    id: int = Field(...)
    username: str = Field(..., max_length=255)


class UserRequest(BaseModel):
    id: int = Field(...)


class RefreshToken(BaseModel):
    refresh_token: str = Field(...)


class TokenPair(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
