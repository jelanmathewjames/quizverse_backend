from ninja import Router

from typing import Any, List

from users.models import User
from users.schemas import UserOutSchema
from utils.authentication import AuthBearer, role_required

router = Router(auth=AuthBearer())

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
