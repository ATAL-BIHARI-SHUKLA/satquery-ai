from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime
from typing import Optional

class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserSignup':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

    @model_validator(mode='after')
    def normalize_email(self) -> 'UserSignup':
        if self.email:
            self.email = self.email.strip().lower()
        return self

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @model_validator(mode='after')
    def normalize_email(self) -> 'UserLogin':
        if self.email:
            self.email = self.email.strip().lower()
        return self

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: datetime

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
