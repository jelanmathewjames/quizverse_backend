from ninja import Router
from typing import Any

from utils.authentication import AuthBearer, role_required

router = Router(auth=AuthBearer())

@router.post("/qbank/", response={200: Any, 400: Any})
@role_required(["Faculty"])
def create_qbank(request):
    pass