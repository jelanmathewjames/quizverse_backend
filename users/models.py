import uuid
from django.db import models


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    username = models.EmailField(max_length=256, unique=True)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=150)
    role = models.ManyToManyField("Role")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user"


class Role(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "role"


class UserInstitutionLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="user_institution_link"
    )
    institution = models.ForeignKey(
        "admin.Institution", on_delete=models.CASCADE, related_name="institution_user_link"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_institution_link"


class UserCommunityLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="user_community_link"
    )
    community = models.ForeignKey(
        "admin.Community", on_delete=models.CASCADE, related_name="community_user_link"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_community_link"


class Token(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    access_token = models.TextField()
    refresh_token = models.TextField()
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "token"


class VerificationToken(models.Model):
    TOKEN_TYPES = [("verify", "verify"), ("forgot", "forgot")]
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    token = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    token_type = models.CharField(max_length=7, choices=TOKEN_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "verification_token"
