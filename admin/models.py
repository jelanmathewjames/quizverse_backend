import uuid
from django.db import models


# Create your models here.
class Institution(models.Model):
    TYPE_CHOICES = [
        ("SCHOOL", "school"),
        ("COLLEGE", "college"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    instituion_type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    education_system = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "institution"


class Community(models.Model):
    LEVEL_CHOICES = [
        ("GLOBAL", "global"),
        ("NATIONAL", "national"),
        ("REGIONAL", "regional"),
        ("LOCAL", "local"),
    ]
    TYPE_CHOICES = [
        ("TECHNICAL", "technical"),
        ("NON-TECHNICAL", "non-technical"),
        ("SERVICE", "service"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    community_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "community"


class Department(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "department"


class Faculty(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    faculty_id = models.CharField(max_length=100)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    institution = models.ForeignKey("Institution", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faculty"


class Student(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    roll_number = models.CharField(max_length=100)
    class_or_semester = models.IntegerField()
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    institution = models.ForeignKey("Institution", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student"


class FacultyDepartmentLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faculty_department_link"


class StudentDepartmentLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_department_link"


class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    handling_faculty = models.ManyToManyField("Faculty")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course"
