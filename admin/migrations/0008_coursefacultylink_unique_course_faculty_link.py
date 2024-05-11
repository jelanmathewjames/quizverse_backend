# Generated by Django 5.0.1 on 2024-05-11 10:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admin", "0007_rename_instituion_type_institution_institution_type"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="coursefacultylink",
            constraint=models.UniqueConstraint(
                fields=("course", "faculty"), name="unique_course_faculty_link"
            ),
        ),
    ]