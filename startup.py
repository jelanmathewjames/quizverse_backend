import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quizverse_backend.settings")
django.setup()

from django.db import IntegrityError
from users.models import Role
from utils.types import UserRoles

"""
    Basic scripts for the proper functioning of the project 
    where the user can't directly be involved.
"""


def create_roles():
    for role in UserRoles.get_roles():
        try:
            Role.objects.create(name=role)
        except IntegrityError:
            print(f"""{role} already exist""")


if __name__ == "__main__":
    create_roles()