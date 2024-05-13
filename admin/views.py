from ninja import Router
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
        role__name="Institution", user_institution_link__institution__id=data.entity_id
    ).exists()
    if any_institution_admin:
        return 400, {"message": "Institution already has an admin"}

    role = Role.objects.get(name="Institution")
    user.role.add(role)
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
        role__name="Community", user_community_link__community__id=data.entity_id
    ).exists()
    if any_community_admin:
        return 400, {"message": "Community already has an admin"}

    role = Role.objects.get(name="Community")
    user.role.add(role)
    UserCommunityLink.objects.create(user=user, community=community, role=role)
    return 200, {"message": "Community role given"}


@router.post("/role/faculty/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_faculty_role(request, data: GiveRolesMembershipSchema):
    user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
    role = Role.objects.get(name="Faculty")
    for datas in data.user_membership_id:
        departments = Department.objects.filter(id=datas.department_ids[0])
        user = User.objects.get(id=datas.user_id)
        user.role.add(role)
        try:
            UserInstitutionLink.objects.create(
                user=user, institution=user_link.institution, role=role
            )
        except IntegrityError:
            return 400, {"message": "User already has role in this institution"}
        faculty = Faculty.objects.create(faculty_id=datas.member_id, user=user)
        for department in departments:
            FacultyDepartmentLink.objects.create(faculty=faculty, department=department)
    return 200, {"message": "Faculty role given"}


@router.post("/role/student/", response={200: Any, 400: Any})
@role_required(["Institution"])
def give_student_role(request, data: GiveRolesMembershipSchema):
    user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
    role = Role.objects.get(name="Student")
    for datas in data.user_membership_id:
        departments = Department.objects.filter(id=datas.department_ids[0])
        user = User.objects.get(id=datas.user_id)
        user.role.add(role)
        try:
            UserInstitutionLink.objects.create(
                user=user, institution=user_link.institution, role=role
            )
        except IntegrityError:
            return 400, {"message": "User already has role in this institution"}
        student = Student.objects.create(
            roll_number=datas.member_id,
            user=user,
            class_or_semester=data.class_or_semester,
        )
        for department in departments:
            StudentDepartmentLink.objects.create(student=student, department=department)
    return 200, {"message": "Student role given"}


@router.post("/role/community-member/", response={200: Any, 400: Any})
@role_required(["Community"])
def give_community_member_role(request, data: GiveRolesSchema):
    users = User.objects.filter(id__in=data.user_ids)
    user_link = get_object_or_404(UserCommunityLink, user__id=request.auth["user"])

    role = Role.objects.get(name="CommunityMember")
    for user in users:
        user.roles.add(role)
        UserCommunityLink.objects.create(
            user=user, community=user_link.community, role=role
        )
    return 200, {"message": "Community Member role given"}


@router.post("/education-system/", response={200: EducationSystemOutSchema, 400: Any})
@role_required(["Admin"])
def create_education_system(request, data: NameSchema):
    data = data.dict()
    if EducationSystem.objects.filter(name=data["name"]).exists():
        return 400, {"message": "Education system with this name already exist"}

    education_system = EducationSystem.objects.create(name=data["name"])
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
def create_department(request, data: NameSchema):
    if Department.objects.filter(name=data.name).exists():
        return 400, {"message": "Department with this name already exist"}

    department = Department.objects.create(name=data.name)
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
    data["course"] = get_object_or_404(Course, id=data.pop("course_id"))
    module = Module.objects.create(**data)
    return 200, module


@router.post("/link/institution-department/", response={200: Any, 400: Any})
@role_required(["Institution"])
def link_institution_department(request, data: InstitutionLink):
    data = data.dict()
    user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
    institution = get_object_or_404(Institution, id=user_link.institution_id)
    for id in data["link_id"]:
        department = get_object_or_404(Department, id=id)
        try:
            InstitutionDepartmentLink.objects.create(
                institution=institution, department=department
            )
        except IntegrityError:
            return 400, {"message": "Department already linked to institution"}
    return 200, {"message": "Department linked to institution"}


@router.post("/link/institution-course/", response={200: Any, 400: Any})
@role_required(["Institution"])
def link_institution_course(request, data: InstitutionLink):
    data = data.dict()
    user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
    institution = get_object_or_404(Institution, id=user_link.institution_id)
    for id in data["link_id"]:
        course = get_object_or_404(Course, id=id)
        try:
            InstitutionCourseLink.objects.create(institution=institution, course=course)
        except IntegrityError:
            return 400, {"message": "Course already linked to institution"}
        return 200, {"message": "Course linked to institution"}


@router.post("/link/faculty-course/", response={200: Any, 400: Any})
@role_required(["Institution"])
def link_faculty_course(request, data: FacultyCourseLinkSchema):
    data = data.dict()
    user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
    institution = get_object_or_404(Institution, id=user_link.institution_id)
    faculty = get_object_or_404(Faculty, id=data["faculty_id"])
    if not UserInstitutionLink.objects.filter(
        user__id=faculty.user.id, institution=institution
    ).exists():
        return 400, {"message": "Faculty does not belong to this institution"}
    course = get_object_or_404(Course, id=data["course_id"])
    if not InstitutionCourseLink.objects.filter(
        institution=institution, course=course
    ).exists():
        return 400, {"message": "Course does not belong to this institution"}
    try:
        CourseFacultyLink.objects.create(faculty=faculty, course=course)
    except IntegrityError:
        return 400, {"message": "Course already linked to faculty"}
    return 200, {"message": "Course linked to faculty"}


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


@router.get("/department", response={200: List[DepartmentOutSchema]})
@role_required(["Admin", "Institution", "Faculty", "Student"])
def get_department(request, search: str = None, status: str = None):
    department = Department.objects.all()
    if "Institution" in request.auth["roles"]:
        institution = UserInstitutionLink.objects.filter(
            user_id=request.auth["user"]
        ).first()
        department_ids = InstitutionDepartmentLink.objects.filter(
            institution_id=institution.institution_id
        ).values_list("department_id", flat=True)
        if status == "linked":
            department = Department.objects.filter(id__in=department_ids)
        elif status == "unlinked":
            department = Department.objects.exclude(id__in=department_ids)
    if "Faculty" in request.auth["roles"]:
        faculty_instance = Faculty.objects.filter(user_id=request.auth["user"]).first()
        faculty_department = FacultyDepartmentLink.objects.filter(
            faculty=faculty_instance
        ).values_list("department_id", flat=True)
        department = Department.objects.filter(id__in=faculty_department)
    if "Student" in request.auth["roles"]:
        student_instance = Student.objects.filter(user_id=request.auth["user"]).first()
        student_department = StudentDepartmentLink.objects.filter(
            student=student_instance
        ).values_list("department_id", flat=True)
        department = Department.objects.filter(id__in=student_department)
    if search:
        department = search_queryset(department, search, ["name"])
    return 200, department


@router.get("/course", response={200: List[CourseOutSchema], 400: Any})
@role_required(["Admin", "Institution", "Faculty", "Student"])
def get_course(request, search: str = None, status: str = None):
    course = Course.objects.all()
    if "Institution" in request.auth["roles"]:
        institution = UserInstitutionLink.objects.filter(
            user_id=request.auth["user"]
        ).first()
        course_ids = InstitutionCourseLink.objects.filter(
            institution_id=institution.institution_id
        ).values_list("course_id", flat=True)
        if status == "linked":
            course = Course.objects.filter(id__in=course_ids)
        elif status == "unlinked":
            course = Course.objects.exclude(id__in=course_ids)
    if "Faculty" in request.auth["roles"]:
        faculty_instance = Faculty.objects.filter(user_id=request.auth["user"]).first()
        course_link = CourseFacultyLink.objects.filter(
            faculty=faculty_instance
        ).values_list("course_id", flat=True)
        course = Course.objects.filter(id__in=course_link)
    if "Student" in request.auth["roles"]:
        user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
        student_instance = Student.objects.filter(user_id=request.auth["user"]).first()
        student_department = StudentDepartmentLink.objects.filter(
            student=student_instance
        ).values_list("department_id", flat=True)
        course_link = CourseDepartmentLink.objects.filter(
            department_id__in=student_department
        ).values_list("course_id", flat=True)
        course = Course.objects.filter(
            class_or_semester=student_instance.class_or_semester, id__in=course_link,
            courseinstitutionlink__institution=user_link.institution
        )
    if search:
        course = search_queryset(
            course,
            search,
            ["name", "code", "education_system_name", "class_or_semester"],
        )
    return 200, course


@router.get("/module", response={200: List[ModuleOutSchema], 400: Any})
@role_required(["Admin", "Institution", "Faculty", "Student"])
def get_modules(request, id: str):
    get_object_or_404(Course, id=id)
    if not (modules := Module.objects.filter(course_id=id).all()):
        return 400, {"message": "No modules found for this course"}
    return 200, modules.order_by("module_number")


@router.get("/faculty", response={200: List[FacultyOutSchema], 400: Any})
@role_required(["Institution"])
def get_faculty(request, search: str = None):
    user_link = get_object_or_404(UserInstitutionLink, user__id=request.auth["user"])
    faculty_user_ids = UserInstitutionLink.objects.filter(
        institution=user_link.institution, role__name="Faculty"
    ).values_list("user_id", flat=True)
    faculty = Faculty.objects.filter(user_id__in=faculty_user_ids)
    if search:
        faculty = search_queryset(faculty, search, ["faculty_id"])
    return 200, faculty


@router.get("/student", response={200: List[StudentOutSchema], 400: Any})
@role_required(["Institution", "Faculty"])
def get_student(request, course_id: str = None, search: str = None):
    student = Student.objects.all()
    if "Institution" in request.auth["roles"]:
        user_link = get_object_or_404(
            UserInstitutionLink, user__id=request.auth["user"]
        )
        student_user_ids = UserInstitutionLink.objects.filter(
            institution=user_link.institution, role__name="Student"
        ).values_list("user_id", flat=True)
        student = student.filter(user_id__in=student_user_ids)
    elif "Faculty" in request.auth["roles"]:
        user_link = get_object_or_404(
            UserInstitutionLink, user__id=request.auth["user"]
        )
        course = get_object_or_404(
            Course,
            id=course_id,
            coursefacultylink__faculty__user_id=request.auth["user"]
        )
        department_ids = CourseDepartmentLink.objects.filter(course=course).values_list(
            "department_id", flat=True
        )
        student_user_ids = StudentDepartmentLink.objects.filter(
            department_id__in=department_ids
        ).values_list("student__user_id", flat=True)
        student_ids = UserInstitutionLink.objects.filter(
            user_id__in=student_user_ids, institution=user_link.institution
        ).values_list("user_id", flat=True)
        student = student.filter(
            user_id__in=student_ids, class_or_semester=course.class_or_semester,
        )
    if search:
        student = search_queryset(student, search, ["roll_number"])
    return 200, student
