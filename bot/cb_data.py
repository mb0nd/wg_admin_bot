from aiogram.filters.callback_data import CallbackData


class UserCallbackData(CallbackData, prefix='user'):
    action: str
    id: int | None
    name: str | None = None