from enum import Enum

class UserRoles(Enum):
    ADMIN = "Admin"
    INSTITUTION = "Institution"
    COMMUNITY = "Community"
    FACULTY = "Faculty"
    STUDENT = "Student"

    @classmethod
    def get_roles(cls):
        return [role.value for role in cls]