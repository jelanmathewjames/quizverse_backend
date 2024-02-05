from ninja import ModelSchema
from users.models import User

class UserOutSchema(ModelSchema):
    class Meta:
        model = User
        fields = '__all__'