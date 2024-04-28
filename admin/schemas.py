import uuid

from ninja import Schema, ModelSchema
from typing import List, Union

from admin.models import *

class UserMembershipIDSchema(Schema):
    member_id: str
    user_id: str
    department_ids: List[str]

class GiveRolesMembershipSchema(Schema):
    entity_id: str
    user_membership_id: List[UserMembershipIDSchema]
    class_or_semester: Union[int, None]

class GiveRolesSchema(Schema):
    entity_id: str
    user_ids: List[str]

class InstitutionInSchema(ModelSchema):
    education_system_id: str

    class Meta:
        model = Institution
        exclude = ["id", "created_at", "updated_at", "education_system"]

class InstitutionOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = Institution
        fields = "__all__"


class EducationSystemOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = EducationSystem
        fields = "__all__"


class CommunityInSchema(ModelSchema):
    
    class Meta:
        model = Community
        exclude = ["id", "created_at", "updated_at"]

class CommunityOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = Community
        fields = "__all__"

class DepartmentOutSchema(ModelSchema):
    id: Union[str, uuid.UUID]

    class Meta:
        model = Department
        fields = "__all__"