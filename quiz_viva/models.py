import uuid
from django.db import models


# Create your models here
class QuizOrViva(models.Model):
    TYPE_CHOICES = [("VIVA", "viva"), ("QUIZ", "quiz")]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    viva_or_quiz = models.CharField(max_length=4, choices=TYPE_CHOICES)
    conductor = models.ForeignKey("users.User", on_delete=models.CASCADE)
    qbank = models.ForeignKey("QuestionBank", on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quiz_or_viva"

class StudentQuizOrVivaLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    student = models.ForeignKey("users.User", on_delete=models.CASCADE)
    quiz_or_viva = models.ForeignKey("QuizOrViva", on_delete=models.CASCADE)
    total_marks = models.IntegerField(default=0)
    marks_obtained = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    malpractice = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_quiz_or_viva_link"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "quiz_or_viva"], name="unique_student_quiz_or_viva"
            )
        ]

class StudentResponse(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    student_quiz_or_viva_link = models.ForeignKey("StudentQuizOrVivaLink", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    option = models.ForeignKey("Options", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_response"
        constraints = [
            models.UniqueConstraint(
                fields=["student_quiz_or_viva_link", "question"], name="unique_student_response"
            )
        ]

class CommunityMemberQuizOrVivaLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    community_member = models.ForeignKey("users.User", on_delete=models.CASCADE)
    quiz_or_viva = models.ForeignKey("QuizOrViva", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "community_member_quiz_or_viva_link"
        constraints = [
            models.UniqueConstraint(
                fields=["community_member", "quiz_or_viva"], name="unique_community_member_quiz_or_viva"
            )
        ]


class QuestionBank(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    creator = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question_bank"


class QBankCourseLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    question_bank = models.ForeignKey("QuestionBank", on_delete=models.CASCADE)
    course = models.ForeignKey("admin.Course", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "qbank_course_link"
        constraints = [
            models.UniqueConstraint(
                fields=["question_bank", "course"], name="unique_course_question_bank"
            )
        ]


class Question(models.Model):
    TYPE_CHOICES = [("MCQ", "mcq"), ("DIRECT", "direct")]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    question_number = models.IntegerField()
    question = models.CharField(max_length=500)
    question_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    qbank = models.ForeignKey("QuestionBank", on_delete=models.CASCADE)
    module = models.ForeignKey("admin.Module", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question"


class Options(models.Model):
    OPTION_CHOICES = [("PLAIN", 0), ("A", 1), ("B", 2), ("C", 3), ("D", 4), ("E", 5)]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    option_number = models.IntegerField(choices=OPTION_CHOICES)
    option = models.CharField(max_length=500)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "options"
