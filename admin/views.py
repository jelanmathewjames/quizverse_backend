from ninja import Router, Form
from typing import Any

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q
from django.db import IntegrityError

from utils.authentication import role_required, AuthBearer
from utils.utils import search_queryset
from admin.schemas import *
from users.models import User, Role, UserInstitutionLink, UserCommunityLink
from admin.models import Institution, Community, EducationSystem

router = Router(auth=AuthBearer())


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
    UserInstitutionLink.objects.create(user=user, institution=institution, role=role)
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
    UserCommunityLink.objects.create(user=user, community=community, role=role)
    return 200, {"message": "Community role given"}


@router.post("/role/faculty/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_faculty_role(request, data: GiveRolesMembershipSchema):
    institution = get_object_or_404(Institution, id=data.entity_id)
    role = Role.objects.get(name="Faculty")
    for datas in data.user_membership_id:
        departments = Department.objects.filter(id__in=datas["department_ids"])
        user = User.objects.get(id=datas["user_id"])
        user.roles.add(role)
        UserInstitutionLink.objects.create(
            user=user, institution=institution, role=role
        )
        faculty = Faculty.objects.create(facutly_id=datas["member_id"], user=user)
        for department in departments:
            FacultyDepartmentLink.objects.create(faculty=faculty, department=department)
    return 200, {"message": "Faculty role given"}


@router.post("/role/student/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_student_role(request, data: GiveRolesMembershipSchema):
    institution = get_object_or_404(Institution, id=data.entity_id)
    role = Role.objects.get(name="Student")
    for datas in data.user_membership_ids:
        departments = Department.objects.filter(id__in=datas["department_ids"])
        user = User.objects.get(id=datas["user_id"])
        user.roles.add(role)
        UserInstitutionLink.objects.create(
            user=user, institution=institution, role=role
        )
        student = Student.objects.create(
            roll_number=datas["member_id"],
            user=user,
            class_or_semester=data["class_or_semester"],
        )
        for department in departments:
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
        UserCommunityLink.objects.create(user=user, community=community, role=role)
    return 200, {"message": "Community Member role given"}


@router.post("/education-system/", response={200: EducationSystemOutSchema, 400: Any})
@role_required(["Admin"])
def create_education_system(request, name: str = Form(...)):
    if EducationSystem.objects.filter(name=name).exists():
        return 400, {"message": "Education system with this name already exist"}

    education_system = EducationSystem.objects.create(name=name)
    return 200, education_system


@router.post("/institution/", response={200: InstitutionOutSchema, 400: Any})
@role_required(["Admin"])
def create_institution(request, data: InstitutionInSchema):
    data = data.dict()
    get_object_or_404(EducationSystem, id=data["education_system_id"])
    if Institution.objects.filter(name=data["name"]).exists():
        return 400, {"message": "Institution with this name already exist"}

    institution = Institution.objects.create(**data)
    return 200, institution


@router.post("/community/", response={200: CommunityOutSchema, 400: Any})
@role_required(["Admin"])
def create_community(request, data: CommunityInSchema):
    data = data.dict()
    if Community.objects.filter(name=data["name"]).exists():
        return 400, {"message": "Community with this name already exist"}

    community = Community.objects.create(**data)
    return 200, community


@router.post("/department/", response={200: DepartmentOutSchema, 400: Any})
@role_required(["Admin"])
def create_department(request, name: str = Form(...)):
    if Department.objects.filter(name=name).exists():
        return 400, {"message": "Department with this name already exist"}

    department = Department.objects.create(name=name)
    return 200, department


@router.post("/course/", response={200: CourseOutSchema, 400: Any})
@role_required(["Admin"])
def create_course(request, data: CourseInSchema):
    data = data.dict()
    department = get_object_or_404(Department, id=data.pop("department_id"))
    get_object_or_404(EducationSystem, id=data["education_system_id"])
    if Course.objects.filter(Q(name=data["name"]) | Q(code=data["code"])).exists():
        return 400, {"message": "Course with this name or code already exists"}

    course = Course.objects.create(**data)
    CourseDepartmentLink.objects.create(course=course, department=department)
    return 200, course


@router.post("/module/", response={200: ModuleOutSchema, 400: Any})
@role_required(["Admin"])
def create_module(request, data: ModuleInSchema):
    data = data.dict()
    get_object_or_404(Course, id=data.get("course_id"))
    module = Module.objects.create(**data)
    return 200, module


@router.post("/link/institution-department/", response={200: Any, 400: Any})
@role_required(["Institution"])
def link_institution_department(
    request, institution_id: str = Form(...), department_id: str = Form(...)
):
    institution = get_object_or_404(Institution, id=institution_id)
    department = get_object_or_404(Department, id=department_id)
    try:
        InstitutionDepartmentLink.objects.create(
            institution=institution, department=department
        )
    except IntegrityError:
        return 400, {"message": "Department already linked to institution"}
    return 200, {"message": "Department linked to institution"}


@router.post("/link/institution-course/", response={200: Any, 400: Any})
@role_required(["Institution"])
def link_institution_course(
    request, institution_id: str = Form(...), course_id: str = Form(...)
):
    institution = get_object_or_404(Institution, id=institution_id)
    course = get_object_or_404(Course, id=course_id)
    try:
        InstitutionCourseLink.objects.create(institution=institution, course=course)
    except IntegrityError:
        return 400, {"message": "Course already linked to institution"}
    return 200, {"message": "Course linked to institution"}


@router.get("/education-system", response={200: List[EducationSystemOutSchema]})
@role_required(["Admin"])
def get_education_system(request, search: str = None):
    education_system = EducationSystem.objects.all()
    if search:
        education_system = search_queryset(education_system, search, ["name"])
    return 200, education_system


@router.get("/institution", response={200: List[InstitutionOutSchema]})
@role_required(["Admin"])
def get_institution(request, search: str = None):
    institution = Institution.objects.all()
    if search:
        institution = search_queryset(institution, search, ["name", "place"])
    return 200, institution


@router.get("/community", response={200: List[CommunityOutSchema]})
@role_required(["Admin"])
def get_community(request, search: str = None):
    community = Community.objects.all()
    if search:
        community = search_queryset(
            community, search, ["name", "level", "community_type"]
        )
    return 200, community


@router.get("/department", response={200: List[CommunityOutSchema]})
@role_required(["Admin", "Institution", "Faculty", "Student"])
def get_department(request, search: str = None):
    department = Department.objects.all()
    if "Faculty" in request.auth["roles"]:
        faculty_instance = Faculty.objects.filter(user_id=request.auth["user"]).first()
        department = Department.objects.prefetch_related(
            Prefetch(
                "faculty_department_link",
                queryset=FacultyDepartmentLink.objects.filter(faculty=faculty_instance),
                to_attr="handled_by_faculty",
            )
        )
    if "Student" in request.auth["roles"]:
        student_instance = Student.objects.filter(user_id=request.auth["user"]).first()
        department = Department.objects.prefetch_related(
            Prefetch(
                "student_department_link",
                queryset=StudentDepartmentLink.objects.filter(student=student_instance),
                to_attr="department",
            )
        )
    if search:
        department = search_queryset(department, search, ["name"])
    return 200, department


@router.get("/course", response={200: Any, 400: Any})
@role_required(["Admin", "Institution", "Faculty"])
def get_course(request, search: str = None):
    course = Course.objects.all()
    if "Faculty" in request.auth["roles"]:
        faculty_instance = Faculty.objects.filter(user_id=request.auth["user"]).first()
        course = Course.objects.prefetch_related(
            Prefetch(
                "course_faculty_link",
                queryset=CourseFacultyLink.objects.filter(faculty=faculty_instance),
                to_attr="handled_by_faculty",
            )
        )
    if "Student" in request.auth["roles"]:
        student_instance = Student.objects.filter(user_id=request.auth["user"]).first()
        department = Department.objects.prefetch_related(
            Prefetch(
                "student_department_link",
                queryset=StudentDepartmentLink.objects.filter(student=student_instance),
                to_attr="department",
            )
        )
        course = Course.objects.prefetch_related(
            Prefetch(
                "course_department_link",
                queryset=CourseDepartmentLink.objects.filter(department=department),
                to_attr="department",
            )
        ).filter(class_or_semester=student_instance.class_or_semester)
    if search:
        course = search_queryset(
            course,
            search,
            ["name", "code", "education_system_name", "class_or_semester"],
        )
    return 200, course
