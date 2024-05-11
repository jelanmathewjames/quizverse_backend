import uuid

from ninja import Schema, ModelSchema
from typing import List, Union

from quiz_viva.models import QuestionBank, Question, Answer
from admin.schemas import CourseOutSchema

class AnswerInSchema(ModelSchema):
    question_id: str
    class Meta:
        model = Answer
        fields = ["id", "question", "created_at", "updated_at"]


class AnswerOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = Answer
        exclude = ["is_correct"]
    
class QuestionOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = Question
        fields = "__all__"

class QuestionInSchema(ModelSchema):
    qbank_id: str
    module_id: str

    class Meta:
        model = Question
        exclude = ["id", "qbank", "created_at", "updated_at"]

class QBankInSchema(Schema):
    title: str
    course_id: str

class QBankOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]
    course: CourseOutSchema = None
    questions: List[QuestionOutSchema] = None
    
    class Meta:
        model = QuestionBank
        fields = "__all__"

class QuizOrVivaInSchema(ModelSchema):

    class Meta:
        model = QuestionBank
        exclude = ["id", "creator", "created_at", "updated_at"]