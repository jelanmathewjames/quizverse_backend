from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from users.models import User, Role


class Command(BaseCommand):
    help = "Create a superuser with a username, email, and password."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            dest="username",
            default=None,
            help="Specifies the username for the superuser.",
        ),
        parser.add_argument(
            "--email",
            dest="email",
            default=None,
            help="Specifies the email address for the superuser.",
        ),
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help=("Specifies the password for the superuser"),
        ),
    

    def handle(self, *args, **options):
        username = options.get("username", None)
        email = options.get("email", None)
        password = options.get("password", None)
        if username and email and password:
            password = make_password(password)
            try:
                role = Role.objects.get(name="Admin")
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                )
                user.save()
                self.stdout.write("Superuser created successfully")
            except Exception as e:
                self.stdout.write(f"Error creating superuser: {e}")
        else:
            self.stdout.write("Please provide username, email, and password")