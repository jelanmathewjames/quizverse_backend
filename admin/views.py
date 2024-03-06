from ninja import Router
from typing import Any

from django.shortcuts import get_object_or_404

from utils.authentication import role_required
from admin.schemas import GiveRolesSchema
from users.models import User, Role, UserInstitutionLink, UserCommunityLink
from admin.models import Institution, Community

router = Router()


@router.post("/institution/", response={200: Any, 400: Any})
@role_required(["Admin"])
def give_institution_role(request, data: GiveRolesSchema):
    if len(data.user_ids) != 1:
        return {"message": "Only one user can be given institution role"}

    user = get_object_or_404(User, id=data.user_ids[0])
    institution = get_object_or_404(Institution, id=data.entity_id)

    any_institution_admin = User.objects.filter(
        roles__name="Institution", user_institution_link__instituion__id=data.entity_id
    ).exists()
    if any_institution_admin:
        return 400, {"message": "Institution already has an admin"}

    role = Role.objects.get(name="Institution")
    user.roles.add(role)
    UserInstitutionLink.objects.create(
        user=user, institution=institution
    )
    return 200, {"message": "Institution role given"}


@router.post("/community/", response={200: Any, 400: Any})
@role_required(["Admin"])
def give_community_role(request, data: GiveRolesSchema):
    if len(data.user_ids) != 1:
        return {"message": "Only one user can be given community role"}
    
    user = get_object_or_404(User, id=data.user_ids[0])
    community = get_object_or_404(Community, id=data.entity_id)

    any_community_admin = User.objects.filter(
        roles__name="Community", user_community_link__community__id=data.entity_id
    ).exists()
    if any_community_admin:
        return 400, {"message": "Community already has an admin"}

    role = Role.objects.get(name="Community")
    user.roles.add(role)
    UserCommunityLink.objects.create(
        user=user, community=community
    )
    return {"message": "Community role given"}


@router.post("/faculty/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_faculty_role(request, data: GiveRolesSchema):
    users = User.objects.filter(id__in=data.user_ids)
    institution = get_object_or_404(Institution, id=data.entity_id)

    role = Role.objects.get(name="Faculty")
    for user in users:
        user.roles.add(role)
        UserInstitutionLink.objects.create(
            user=user, institution=institution
        )
    return 200, {"message": "Faculty role given"}


@router.post("/student/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_student_role(request, data: GiveRolesSchema):
    users = User.objects.filter(id__in=data.user_ids)
    institution = get_object_or_404(Institution, id=data.entity_id)

    role = Role.objects.get(name="Student")
    for user in users:
        user.roles.add(role)
        UserInstitutionLink.objects.create(
            user=user, institution=institution
        )
    return {"message": "Student role given"}


@router.post("/community-member/", response={200: Any, 400: Any})
@role_required(["Community"])
def give_community_member_role(request, data: GiveRolesSchema):
    users = User.objects.filter(id__in=data.user_ids)
    community = get_object_or_404(Community, id=data.entity_id)

    role = Role.objects.get(name="CommunityMember")
    for user in users:
        user.roles.add(role)
        UserCommunityLink.objects.create(
            user=user, community=community
        )
    return {"message": "Community Member role given"}
