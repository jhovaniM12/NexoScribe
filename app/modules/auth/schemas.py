from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    image_url: str | None = None


class AuthUserData(BaseModel):
    user: UserResponse


class AuthUserResponse(BaseModel):
    success: bool = True
    data: AuthUserData