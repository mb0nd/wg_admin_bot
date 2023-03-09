from pydantic import BaseModel, IPvAnyNetwork
from datetime import datetime


class WGUserModel(BaseModel):
    peer: str | None
    endpoint: str | None
    allowed_ips: IPvAnyNetwork
    latest_handshake: int | None
    received: int | None
    send: int | None

class DBUserModel(BaseModel):
    user_id: int
    user_name: str
    pub_key: str
    ip: str
    is_baned: bool
    is_pay: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserModel(WGUserModel, DBUserModel):
    pass


