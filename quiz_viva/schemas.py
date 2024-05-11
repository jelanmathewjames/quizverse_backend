import uuid

from ninja import Schema, ModelSchema
from typing import List, Union

from quiz_viva.models import QuestionBank, Question, QuizOrViva, Options
from admin.schemas import CourseOutSchema

class OptionInSchema(ModelSchema):

    class Meta:
        model = Options
        exclude = ["id", "question", "created_at", "updated_at"]
    
class QuestionOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]
    options: List[OptionInSchema] = None
    class Meta:
        model = Question
        fields = "__all__"

class QuestionInSchema(ModelSchema):
    qbank_id: str
    module_id: str
    options: List[OptionInSchema]

    class Meta:
        model = Question
        exclude = ["id", "qbank", "module", "created_at", "updated_at"]

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
    qbank_id: str
    class Meta:
        model = QuizOrViva
        exclude = ["id", "conductor", "qbank", "is_private", "created_at", "updated_at"]
    
class QuizOrVivaOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = QuizOrViva
        fields = "__all__"

