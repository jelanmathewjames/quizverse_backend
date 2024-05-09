from ninja import Router
from typing import Any

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from quiz_viva.schemas import *
from quiz_viva.models import *
from admin.models import Course, Module
from utils.authentication import AuthBearer, role_required

router = Router(auth=AuthBearer())


@router.post("/qbank/", response={200: Any, 400: Any})
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
    qbank = get_object_or_404(QuestionBank, id=data.qbank_id, creator_id=request.auth["user"])
    module = get_object_or_404(Module, id=data.module_id)
    question = Question.objects.create(
        question=data.question,
        options=data.options,
        correct_option=data.correct_option,
        qbank=qbank,
    )
    QuestionModuleLink.objects.create(question=question, module=module)
    return 200, question


@router.get("/question", response={200: List[QuestionOutSchema], 400: Any})
@role_required(["Faculty"])
def get_question(request, qbank_id: str):
    question = Question.objects.filter(
        qbank_id=qbank_id, qbank__creator_id=request.auth["user"]
    ).all()
    return 200, question


@router.post("/answer/", response={200: AnswerOutSchema, 400: Any})
@role_required(["Faculty"])
def create_answer(request, data: AnswerInSchema):
    question = get_object_or_404(Question, id=data.question_id)
    answer = Answer.objects.create(
        question=question, answer=data.answer, is_correct=data.is_correct
    )
    return 200, answer

@router.get("/answer", response={200: List[AnswerOutSchema], 400: Any})
@role_required(["Faculty"])
def get_answer(request, question_id: str):
    answer = Answer.objects.filter(question_id=question_id).all()
    return 200, answer
