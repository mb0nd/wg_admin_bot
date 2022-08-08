from email.message import Message
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Message
import os



class IsAdminMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.admin_id = int(os.getenv('ADMIN_ID'))

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if data['event_from_user'].id != self.admin_id:
            return await handler(event, data)
        return
        # возможно добавить запись в лог, если кто то ломится в админские команды