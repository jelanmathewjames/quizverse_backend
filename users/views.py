import secrets
import re
from ninja import Router, Form
from typing import Any, List

from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

from users.models import *
from users.schemas import *
from quizverse_backend.settings import PASSWORD_REGEX, EMAIL_HOST_USER
from utils.authentication import AuthBearer, role_required, verify_token, generate_access_token, generate_token

router = Router(auth=AuthBearer())


def otp_generator(length):
    return secrets.randbelow(10**length)

def verification_email(email):
    otp = otp_generator(6)
    subject = 'Email Verification'
    message = f'Your OTP is {otp}. Please verify your email.'
    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)
    return otp

@router.get("/user", response={200: UserOutSchema, 404: Any})
def get_user(request):
    try:
        user = User.objects.get(id=request.auth.user_id)
        return 200, user
    except User.DoesNotExist:
        return 404, {"details": "User not found"}


@router.get("/users", response={201: List[UserOutSchema]})
@role_required(["Admin"])
def get_users(request):
    users = User.objects.all()
    return 201, users


@router.post("/register/", response={201: UserOutSchema, 400: Any})
def register(request, user: UserInSchema):
    unique_fields = ["username", "email"]
    user_data = user.dict()
    for field in unique_fields:
        if User.objects.filter(**{field: user_data[field]}).exists():
            return 400, {"details": f"{field} already exists"}
    if not re.match(PASSWORD_REGEX, user_data["password"]):
        return 400, {
            "details": """Password is weak and must contain 
            at least 8 characters, 1 uppercase, 1 lowercase, 
            1 number and 1 special character"""
        }
    user_data["password"] = make_password(user_data["password"])
    user = User.objects.create(**user_data)
    otp = verification_email(user.email)
    VerificationToken.objects.create(user=user, otp=otp)
    return 201, user


@router.post("/verify/", response={200: Any, 400: Any})
def send_verification(request):
    user_id = request.auth.user_id
    user = User.objects.get(id=user_id)
    otp = verification_email(user.email)
    VerificationToken.objects.update_or_create(user=user, defaults={"user":user, "otp": otp})
    return 200, {"details": "Verification email sent"}


@router.post("/verify/{otp}/", response={200: Any, 400: Any})
def verify_otp(request, otp: int):
    user_id = request.auth.user_id
    user = User.objects.get(id=user_id)
    verification_token = VerificationToken.objects.get(user=user)
    if otp == verification_token.otp:
        user.is_verified = True
        user.save()
        return 200, {"details": "Email verified"}
    return 400, {"details": "Invalid OTP"}


@router.post("/login/", auth=None, response={200: TokenSchema, 400: Any})
def login(request, login: LoginSchema):
    user_data = login.dict()
    user = User.objects.filter(
        Q(username=user_data["username_or_email"]) | Q(email=user_data["username_or_email"])
    ).first()

    if user and check_password(user_data["password"], user.password):
        access_token, refresh_token = generate_token(user.id, [role.name for role in user.role.all()])
        return 200, {"access_token": access_token, "refresh_token": refresh_token}
    
    return 400, {"details": "Invalid credentials"}

@router.post("/logout/", response={200: Any, 400: Any})
def logout(request):
    data = request.auth
    Token.objects.filter(
        user_id=data["user_id"], access_token=data["token"]
    ).delete()
    return 200, {"message": "Logout successful"}
    

@router.post("/get-access-token/", response={200: TokenSchema, 400: Any})
def get_access_token(request, refresh_token: str = Form(...)):
    try:
        payload = verify_token(refresh_token, "refresh")
        if payload is None:
            return 400, {
                "message": "Invalid token",
                "code": 400,
                "details": {"error": "Token is invalid or expired"},
            }
        user_id = payload["user_id"]
        role = payload["role"]
        access_token = generate_access_token(user_id, role)
        Token.objects.filter(user_id=user_id, refresh_token=refresh_token).update(
            access_token=access_token
        )
        return 200, {"access_token": access_token, "refresh_token": refresh_token}
    except Exception as e:
        return 400, {
            "message": "Invalid token",
            "code": 400,
            "details": {"error": str(e)},
        }