import secrets
import re
from datetime import datetime, timedelta

from ninja import Router, Form
from typing import Any, List
from pydantic import EmailStr

from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import get_template

from users.models import *
from users.schemas import *
from quizverse_backend.settings import PASSWORD_REGEX, EMAIL_HOST_USER, FRONTEND_URL
from utils.authentication import (
    AuthBearer,
    role_required,
    verify_token,
    generate_access_token,
    generate_token,
)

router = Router(auth=AuthBearer())


def verification_email(email):
    token = secrets.token_urlsafe(40)
    subject = "Email Verification"
    email_template = get_template("resetPassword.html")
    context = {"verification_link": f"{FRONTEND_URL}/verify/{token}"}
    email_str = email_template.render(context)
    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(
        subject,
        message="",
        html_message=email_str,
        from_email=from_email,
        recipient_list=recipient_list,
    )
    return token


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


@router.post("/register/", auth=None, response={201: UserOutSchema, 400: Any})
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
    token = verification_email(user.email)
    VerificationToken.objects.create(user=user, token=token, token_type="verify")
    return 201, user


@router.post("/verify/", response={200: Any, 400: Any})
def send_verification(request):
    user_id = request.auth.user_id
    user = User.objects.get(id=user_id)
    if user.is_verified:
        return 400, {"details": "Email already verified"}

    token = verification_email(user.email)
    VerificationToken.objects.create(user=user, token=token, token_type="verify")
    return 200, {"details": "Verification email sent"}


@router.post("/verify/{token}/", response={200: Any, 400: Any})
def verify_email(request, token: str):
    try:
        verification_token = VerificationToken.objects.get(
            token=token, token_type="verify"
        )
    except VerificationToken.DoesNotExist:
        return 400, {"details": "Invalid Link"}
    if datetime.now() > verification_token.created_at + timedelta(minutes=5):
        return 400, {"details": "Link Expired"}

    token.user.is_verified = True
    token.user.save()
    verification_token.delete()
    return 200, {"details": "Email verified"}


@router.post("/login/", auth=None, response={400: Any})
def login(request, login: LoginSchema):
    user_data = login.dict()
    user = User.objects.filter(
        Q(username=user_data["username_or_email"])
        | Q(email=user_data["username_or_email"])
    ).first()

    if user and check_password(user_data["password"], user.password):
        access_token, refresh_token = generate_token(
            user.id, [role.name for role in user.role.all()]
        )
        Token.objects.create(
            user_id=user.id, access_token=access_token, refresh_token=refresh_token
        )
        response = JsonResponse(data={"access_token": access_token}, status=200)
        response.set_cookie("refresh_token", refresh_token, httponly=True)
        return response

    return 400, {"details": "Invalid credentials"}


@router.post("/logout/", response={200: Any, 400: Any})
def logout(request):
    data = request.auth
    Token.objects.filter(user_id=data["user_id"], access_token=data["token"]).delete()
    return 200, {"message": "Logout successful"}


@router.post("/refresh/", auth=None, response={200: TokenSchema, 400: Any})
def get_access_token(request):
    try:
        refresh_token = request.COOKIES.get("refresh_token")
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
        return 200, {"access_token": access_token}
    except Exception as e:
        return 400, {
            "message": "Invalid token",
            "code": 400,
            "details": {"error": str(e)},
        }


@router.post("/reset-password/", response={200: Any, 400: Any, 500: Any})
def reset_password(request, payload: ResetPasswordSchema):
    user = User.objects.get(id=request.auth["user_id"])
    if not check_password(payload.current_password, user.password):
        return 400, {
            "message": "Invalid current password",
            "code": 400,
            "details": {"current_password": ["Password is incorrect"]},
        }
    if check_password(payload.new_password, user.password):
        return 400, {
            "message": "Invalid new password",
            "code": 400,
            "details": {"new_password": ["New password must be different"]},
        }
    user.password = make_password(payload.new_password)
    user.save()
    return 200, {"message": "Reset password successful"}


@router.post("/forgot-password/", auth=None, response={200: Any, 400: Any})
def forgot_password(request, email: EmailStr = Form(...)):
    user = User.objects.filter(email=email).first()
    if user:
        token = secrets.token_urlsafe(40)
        VerificationToken.objects.create(user=user, token=token, token_type="forgot")
        subject = "Forgot Password"
        message = f"Your reset password link is {FRONTEND_URL}/reset/{token}. Please reset your password."
        from_email = EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
        return 200, {"message": "Email sent"}
    return 400, {"message": "Email not found"}


@router.post("/forgot-password/{token}/", auth=None, response={200: Any, 400: Any})
def verify_forgot_otp(request, token: str, new_password: str = Form(None)):
    try:
        verification_token = VerificationToken.objects.get(
            token=token, token_type="forgot"
        )
    except VerificationToken.DoesNotExist:
        return 400, {"details": "Invalid link"}
    if datetime.now() > verification_token.created_at + timedelta(minutes=2):
        return 400, {"details": "Link expired"}
    if new_password:
        user = verification_token.user
        user.password = make_password(new_password)
        user.save()
        return 200, {"message": "Password reset successfully"}
    return 200, {"details": "Valid link"}


@router.get("/role-requests", response={200: List[RoleRequests]})
def get_role_request(request):
    user_institution = list(
        UserInstitutionLink.objects.filter(
            user_id=request.auth.user_id, accepted=False
        ).values_list("institution__name", "role__name")
    )
    user_community = list(
        UserCommunityLink.objects.filter(
            user_id=request.auth.user_id, accepted=False
        ).values_list("community__name", "role__name")
    )
    user_institution = [
        {"entity": "Institution", "entity_name": x[0], "role": x[1]}
        for x in user_institution
    ]
    user_community = [
        {"entity": "Community", "entity_name": x[0], "role": x[1]}
        for x in user_community
    ]
    return 200, user_institution + user_community


@router.post("/accept-role/", response={200: Any, 400: Any})
def accept_role(request, role: str, entity: str, entity_name: str):
    if entity == "Institution":
        user_institution = UserInstitutionLink.objects.get(
            user_id=request.auth.user_id,
            institution__name=entity_name,
            role__name=role,
            accepted=False,
        )
        user_institution.accepted = True
        user_institution.save()
    elif entity == "Community":
        user_community = UserCommunityLink.objects.get(
            user_id=request.auth.user_id,
            community__name=entity_name,
            role__name=role,
            accepted=False,
        )
        user_community.accepted = True
        user_community.save()
    return 200, {"message": "Role accepted"}
