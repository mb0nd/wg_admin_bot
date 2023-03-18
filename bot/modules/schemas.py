from pydantic import BaseModel
from datetime import datetime


class WGUserModel(BaseModel):
    endpoint: str = 'нет данных'
    latest_handshake: datetime | str = 'нет данных'
    received: int = 0
    send: int = 0