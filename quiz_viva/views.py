from ninja import Router

from utils.authentication import AuthBearer, role_required

router = Router()

@router.get("/hello")
def get_hello(request):
    return {"message": "Hello"}