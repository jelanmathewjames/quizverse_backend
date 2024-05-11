from ninja import Router
from typing import Any

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from quiz_viva.schemas import *
from quiz_viva.models import *
from admin.models import Course, Module, Student
from utils.authentication import AuthBearer, role_required

router = Router(auth=AuthBearer())


@router.post("/qbank/", response={200: QBankOutSchema, 400: Any})
@role_required(["Faculty"])
def create_qbank(request, data: QBankInSchema):
    creator_id = request.auth["user"]
    course = get_object_or_404(Course, id=data.course_id)
    qbank = QuestionBank.objects.create(title=data.title, creator_id=creator_id)
    QBankCourseLink.objects.create(question_bank=qbank, course=course)
    return 200, qbank


@router.get("/qbank", response={200: List[QBankOutSchema], 400: Any})
@role_required(["Faculty"])
def get_qbank(request):
    question_bank = QuestionBank.objects.filter(
        creator_id=request.auth["user"]
    ).prefetch_related(
        Prefetch(
            "qbank_course_link",
            queryset=QBankCourseLink.objects.all(),
            to_attr="course",
        ),
        Prefetch("question", queryset=Question.objects.all(), to_attr="questions"),
    )
    return 200, question_bank


@router.get("/question/", response={200: QuestionOutSchema, 400: Any})
@role_required(["Faculty"])
def create_question(request, data: QuestionInSchema):
    data = data.dict()
    qbank = get_object_or_404(
        QuestionBank, id=data.qbank_id, creator_id=request.auth["user"]
    )
    module = get_object_or_404(Module, id=data.module_id)
    question = Question.objects.create(
        question_number=data.question_number,
        question=data.question,
        question_type=data.question_type,
        qbank=qbank,
        module=module
    )
    for option in data.options:
        Options.objects.create(question=question, **option.dict())
    return 200, question


@router.get("/question", response={200: List[QuestionOutSchema], 400: Any})
@role_required(["Faculty"])
def get_question(request, qbank_id: str):
    question = Question.objects.filter(
        qbank_id=qbank_id, qbank__creator_id=request.auth["user"]
    ).all()
    return 200, question


@router.post("/viva/", response={200: QuizOrVivaOutSchema, 400: Any})
@role_required(["Faculty"])
def create_quiz_or_viva(request, data: QuizOrVivaInSchema):
    data = data.dict()
    data["conductor_id"] = request.auth["user"]
    data["qbank"] = get_object_or_404(QuestionBank, id=data.pop("qbank_id"))
    data["is_private"] = True
    quiz_or_viva = QuizOrViva.objects.create(**data)
    return 200, quiz_or_viva

@router.get("/viva", response={200: List[QuizOrVivaOutSchema], 400: Any})
@role_required(["Faculty", "Student"])
def get_viva(request):
    quiz_or_viva = QuizOrViva.objects.all()
    if "Faculty" in request.auth["role"]:
        quiz_or_viva = quiz_or_viva.filter(conductor_id=request.auth["user"])
    elif "Student" in request.auth["role"]:
        student = get_object_or_404(Student, user_id=request.auth["user"])
        quiz_or_viva = quiz_or_viva.filter(
            studentquizorvivalink__student_id=student.id
        )
    quiz_or_viva = QuizOrViva.objects.filter(
        conductor_id=request.auth["user"]
    ).all()
    return 200, quiz_or_viva