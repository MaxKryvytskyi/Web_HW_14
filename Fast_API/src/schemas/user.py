from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, HttpUrl


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=12)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: HttpUrl
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: HttpUrl
    created_at: datetime
    detail: str = "User successfully created"

    class Config:
        from_attributes = True
        # orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
