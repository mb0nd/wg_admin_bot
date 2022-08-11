from aiogram.dispatcher.filters.callback_data import CallbackData
from typing import Union

class UserCallbackData(CallbackData, prefix='user'):
    action: str
    id: int
    name: Union[str, None]