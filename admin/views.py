from ninja import Router
from typing import Any

from django.shortcuts import get_object_or_404

from utils.authentication import role_required
from admin.schemas import *
from users.models import User, Role, UserInstitutionLink, UserCommunityLink
from admin.models import Institution, Community, EducationSystem

router = Router()


@router.post("/role/institution/", response={200: Any, 400: Any})
@role_required(["Admin"])
def give_institution_role(request, data: GiveRolesSchema):
    if len(data.user_ids) != 1:
        return 400, {"message": "Only one user can be given institution role"}

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


@router.post("/role/community/", response={200: Any, 400: Any})
@role_required(["Admin"])
def give_community_role(request, data: GiveRolesSchema):
    if len(data.user_ids) != 1:
        return 400, {"message": "Only one user can be given community role"}
    
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
    return 200, {"message": "Community role given"}


@router.post("/role/faculty/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_faculty_role(request, data: GiveRolesMembershipSchema):
    institution = get_object_or_404(Institution, id=data.entity_id)
    department = get_object_or_404(Department, id=data.department_id)
    role = Role.objects.get(name="Faculty")
    for datas in data.user_membership_id:
        user = User.objects.get(id=datas['user_id'])
        user.roles.add(role)
        UserInstitutionLink.objects.create(
            user=user, institution=institution
        )
        faculty = Faculty.objects.create(facutly_id=datas['member_id'], user=user)
        FacultyDepartmentLink.objects.create(faculty=faculty, department=department)
    return 200, {"message": "Faculty role given"}


@router.post("/role/student/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_student_role(request, data: GiveRolesMembershipSchema):
    institution = get_object_or_404(Institution, id=data.entity_id)
    department = get_object_or_404(Department, id=data.department_id)
    role = Role.objects.get(name="Student")
    for datas in data.user_membership_ids:
        user = User.objects.get(id=datas['user_id'])
        user.roles.add(role)
        UserInstitutionLink.objects.create(
            user=user, institution=institution
        )
        student = Student.objects.create(
            roll_number=datas['member_id'], 
            user=user,
            class_or_semester=data['class_or_semester']
        )
        StudentDepartmentLink.objects.create(student=student, department=department)
    return 200, {"message": "Student role given"}


@router.post("/role/community-member/", response={200: Any, 400: Any})
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
    return 200, {"message": "Community Member role given"}

@router.post("/education-system/", response={200: EducationSystemOutSchema, 400: Any})
@role_required(["Admin"])
def create_education_system(request, name: str):
    if EducationSystem.objects.filter(name=name).exists():
        return 400, {"message": "Education system with this name already exist"}
    
    education_system = EducationSystem.objects.create(name=name)
    return 200, education_system

@router.post("/institution/", response={200: InstitutionOutSchema, 400: Any})
@role_required(["Admin"])
def create_institution(request, data: InstitutionInSchema):
    data = data.dict()
    get_object_or_404(EducationSystem, id=data['education_system_id'])
    if Institution.objects.filter(name=data['name']).exists():
        return 400, {"message": "Institution with this name already exist"}
    
    institution = Institution.objects.create(**data)
    return 200, institution

@router.post("/community/", response={200: CommunityOutSchema, 400: Any})
@role_required(["Admin"])
def create_institution(request, data: CommunityInSchema):
    data = data.dict()
    if Community.objects.filter(name=data['name']).exists():
        return 400, {"message": "Community with this name already exist"}
    
    community = Community.objects.create(**data)
    return 200, community

@router.post("/department/", response={200: DepartmentOutSchema, 400: Any})
@role_required(["Admin"])
def create_department(request, name: str):
    if Department.objects.filter(name=name).exists():
        return 400, {"message": "Department with this name already exist"}
    
    department = Department.objects.create(name=name)
    return 200, department