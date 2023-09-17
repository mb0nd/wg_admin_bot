from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta


class WGUserModel(BaseModel):
    endpoint: str = 'нет данных'
    latest_handshake: int | str = 'нет данных'
    received: float = 0
    send: float = 0

    @field_validator('latest_handshake')
    @classmethod
    def convert_to_datetime(cls, value):
        if value.isdigit():
            return datetime.fromtimestamp(int(value)).strftime("%H:%M:%S %d.%m.%Y")
        else:
            return value