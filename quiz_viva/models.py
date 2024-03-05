import uuid
from django.db import models


# Create your models here
class VivaOrQuiz(models.Model):
    TYPE_CHOICES = [("VIVA", "viva"), ("QUIZ", "quiz")]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    viva_quiz_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "viva_or_quiz"


class Question(models.Model):
    TYPE_CHOICES = [("MCQ", "mcq"), ("DIRECT", "direct")]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    question_number = models.IntegerField()
    question = models.CharField(max_length=500)
    question_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    viva_or_quiz = models.ForeignKey("VivaOrQuiz", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question"


class Answer(models.Model):
    ANSWER_CHOICES = [("PLAIN", 0), ("A", 1), ("B", 2), ("C", 3), ("D", 4), ("E", 5)]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    answer_number = models.IntegerField(choices=ANSWER_CHOICES)
    answer = models.CharField(max_length=500)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            db_table = "answer"