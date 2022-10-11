from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any, Union
from aiogram.types import Update, user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy import select
from db.models import User


class IsBanedMiddleware(BaseMiddleware):
    """Проверяет каждый запрос от пользователя на предмет бана этого пользователя
       если забанен, сбрасывает обработку запроса
    """
    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], 
        event: Update, 
        data: Dict[str, Any]
    ) -> Any:
        telegram_user: Union[user.User, None] = data.get('event_from_user')
        if not telegram_user:
            return await handler(event, data)
        session: AsyncSession = data['session']
        stmt = select(User.is_baned).filter_by(user_id = telegram_user.id)
        result: ChunkedIteratorResult = await session.execute(stmt)
        find_baned_user: bool = result.scalars().first()
        if find_baned_user:
            if event.event_type == 'callback_query':
                return await event.callback_query.answer()
            return
        return await handler(event, data)