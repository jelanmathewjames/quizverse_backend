from ninja import Router

from utils.authentication import AuthBearer, role_required

router = Router(auth=AuthBearer())

