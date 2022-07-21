from aiogram.dispatcher.filters.callback_data import CallbackData

class UserCallbackData(CallbackData, prefix='user'):
    action: str
    id: int
    name: str
    full_name: str