import jwt
from datetime import datetime, timedelta
from quizverse_backend.settings import SECRET_KEY, JWT_ALGORITHM
from users.models import Token
from quizverse_backend.urls import api
from functools import wraps
from ninja.security import HttpBearer


class InvalidToken(Exception):
    pass


class InSufficientPermission(Exception):
    pass


@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(
        request, {"detail": "Invalid token supplied"}, status=401
    )


@api.exception_handler(InSufficientPermission)
def on_insufficient_permission(request, exc):
    return api.create_response(
        request, {"detail": "Insufficient permission"}, status=403
    )


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        payload = verify_token(token, "access")
        if payload:
            return payload
        else:
            raise InvalidToken


# Function to generate a JWT token
def generate_access_token(user_id, role):
    # Set the expiration time for the token (e.g., 1 hour from now)
    access_exp_time = datetime.utcnow() + timedelta(hours=1)
    # Create the payload containing the user ID and expiration time
    access_payload = {
        "user_id": user_id,
        "exp": access_exp_time,
        "role": role,
        "tokenType": "access",
    }
    # Generate the token using the secret key
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return access_token


def generate_token(user_id, role):
    access_token = generate_access_token(user_id, role)
    refresh_exp_time = datetime.utcnow() + timedelta(days=7)
    # Create the payload containing the user ID and expiration time
    refresh_payload = {
        "user_id": user_id,
        "exp": refresh_exp_time,
        "role": role,
        "tokenType": "refresh",
    }
    # Generate the token using the secret key
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return access_token, refresh_token


# Function to verify a JWT token
def verify_token(token, type):
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHM)

        # Extract the user ID from the payload
        user_id = payload["user_id"]

        # Check if token present in database
        if type == "access":
            if payload["tokenType"] != "access":
                raise jwt.InvalidTokenError
            Token.objects.get(user_id=user_id, access_token=token)
        elif type == "refresh":
            if payload["tokenType"] != "refresh":
                raise jwt.InvalidTokenError
            Token.objects.get(user_id=user_id, refresh_token=token)

        payload["token"] = token
        return payload

    except Token.DoesNotExist:
        # Token not present in database
        return None
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if getattr(request, "auth", {}).get("role") in roles:
                return view_func(request, *args, **kwargs)
            else:
                raise InSufficientPermission

        return wrapper

    return decorator
