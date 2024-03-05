from ninja import Router
from typing import Any

from utils.authentication import role_required
from admin.schemas import GiveRolesSchema
from users.models import User, Role

router = Router()


@router.post("/institution/", response={200: Any, 403: Any})
@role_required(["Admin"])
def give_institution_role(request, data: GiveRolesSchema):
    users = User.object.filter(id__in=data.user_ids)
    return {"message": "Institution role given"}


@router.post("/community/")
@role_required(["Admin"])
def give_community_role(request):
    return {"message": "Community role given"}


@router.post("/faculty/")
@role_required(["Institution"])
def give_faculty_role(request):
    return {"message": "Faculty role given"}


@router.post("/student/")
@role_required(["Institution"])
def give_student_role(request):
    return {"message": "Student role given"}


@router.post("/community-member/")
@role_required(["Community"])
def give_community_member_role(request):
    return {"message": "Community Member role given"}
