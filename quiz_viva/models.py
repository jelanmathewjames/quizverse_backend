from django.db import models

# Create your models here
class VivaOrQuiz(models.Model):
    TYPE_CHOICES = [
        ("VIVA", "Viva"),
        ("QUIZ", "Quiz")
    ]

    title = models.CharField(max_length=50)
    viva_quiz_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Question(models.Model):
    TYPE_CHOICES = [
        ("MCQ", "mcq"),
        ("DIRECT", "direct")
    ] 
    question_number = models.IntegerField()
    question = models.CharField(max_length=500)
    question_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    viva_or_quiz = models.ForeignKey("VivaOrQuiz", on_delete=models.CASCADE)
    