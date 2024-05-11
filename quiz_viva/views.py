from ninja import Router
from typing import Any
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.utils import timezone

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
        module=module,
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
    for student_id in data["student_id"]:
        student = get_object_or_404(Student, id=student_id)
        StudentQuizOrVivaLink.objects.create(student=student, quiz_or_viva=quiz_or_viva)
    return 200, quiz_or_viva


@router.get("/viva", response={200: List[QuizOrVivaOutSchema], 400: Any})
@role_required(["Faculty", "Student"])
def get_viva(request):
    quiz_or_viva = QuizOrViva.objects.all()
    if "Faculty" in request.auth["role"]:
        quiz_or_viva = quiz_or_viva.filter(conductor_id=request.auth["user"])
    elif "Student" in request.auth["role"]:
        student = get_object_or_404(Student, user_id=request.auth["user"])
        quiz_or_viva = quiz_or_viva.filter(studentquizorvivalink__student_id=student.id)
    quiz_or_viva = QuizOrViva.objects.filter(conductor_id=request.auth["user"]).all()
    return 200, quiz_or_viva


@router.post("/response/", response={200: StudentResponseOutSchema, 400: Any})
@role_required(["Student"])
def create_response(request, data: StudentResponseInSchema):
    user_link = get_object_or_404(Student, user_id=request.auth["user"])
    quiz_or_viva = get_object_or_404(QuizOrViva, id=data.quiz_or_viva_id)
    if not (quiz_or_viva.start_time <= timezone.now() < quiz_or_viva.end_time):
        return 400, {"detail": "Viva is over"}

    student_quiz_or_viva_link = get_object_or_404(
        StudentQuizOrVivaLink,
        quiz_or_viva_id=data.quiz_or_viva_id,
        student=user_link,
    )
    if student_quiz_or_viva_link.malpractice or data.malpractice:
        student_quiz_or_viva_link.malpractice = True
        student_quiz_or_viva_link.save()
        return 400, {"detail": "Malpractice detected you can't submit the response"}
    
    if student_quiz_or_viva_link.start_time is None:
        student_quiz_or_viva_link.start_time = timezone.now()
    else:
        end_time = student_quiz_or_viva_link.start_time + timedelta(
            minutes=quiz_or_viva.duration
        )
        if timezone.now() > end_time:
            return 400, {"detail": "Time over"}

    question = get_object_or_404(Question, id=data.question_id)
    option = get_object_or_404(Options, id=data.option_id)
    StudentResponse.objects.create(
        student_quiz_or_viva_link=student_quiz_or_viva_link,
        question=question,
        option=option,
    )
    if option.is_correct:
        student_quiz_or_viva_link.marks_obtained += question.marks
    student_quiz_or_viva_link.save()
