import uuid

from ninja import ModelSchema, Schema
from pydantic import EmailStr
from typing import Union

from users.models import User


class UserOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = User
        exclude = ["password"]


class UserInSchema(Schema):
    username: str
    email: EmailStr
    password: str


class LoginSchema(Schema):
    username_or_email: str
    password: str


class TokenSchema(Schema):
    access_token: str


class ResetPasswordSchema(Schema):
    current_password: str
    new_password: str
