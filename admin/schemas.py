from ninja import Schema
from typing import List

class GiveRolesSchema(Schema):
    entity_id: str
    user_ids: List[str]
    