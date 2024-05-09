import uuid

from ninja import Schema, ModelSchema
from typing import List, Union

from quiz_viva.models import QuestionBank, Question
from admin.schemas import CourseOutSchema

class QuestionsOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = Question
        fields = "__all__"

class QBankInSchema(Schema):
    title: str
    course_id: str

class QBankOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]
    course: CourseOutSchema = None
    questions: List[QuestionsOutSchema]
    
    class Meta:
        model = QuestionBank
        fields = "__all__"