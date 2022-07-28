from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

class DbSessionMiddleware(BaseMiddleware):

    def __init__(self, session_maker, bot):
        super().__init__()
        self.session_maker = session_maker
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:

        data["session_maker"] = self.session_maker
        data['bot'] = self.bot
        return await handler(event, data)