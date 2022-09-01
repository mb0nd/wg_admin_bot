from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Update


class DbSessionMiddleware(BaseMiddleware):
    """Прокидывает сессию с БД в хендлеры"""
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with data['session_maker']() as session:
            data['session'] = session
            return await handler(event, data)