from ninja import Router
from typing import Any

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from quiz_viva.schemas import *
from quiz_viva.models import *
from admin.models import Course
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
        Prefetch(
            "question",
            queryset=Question.objects.all(),
            to_attr="questions"
        )
    )
    return 200, question_bank
