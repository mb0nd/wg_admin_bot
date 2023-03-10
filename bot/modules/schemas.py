from pydantic import BaseModel, IPvAnyAddress, IPvAnyInterface
from datetime import datetime


class WGUserModel(BaseModel):
    peer: str | None
    endpoint: str = 'нет данных'
    latest_handshake: datetime | str = None
    received: int = 0
    send: int = 0

class DBUserModel(BaseModel):
    user_id: int
    user_name: str
    ip: IPvAnyAddress
    is_baned: bool
    is_pay: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True