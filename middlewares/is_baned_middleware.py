from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any, Union
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User


class IsBanedMiddleware(BaseMiddleware):
    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], 
        event: Update, 
        data: Dict[str, Any]
    ) -> Any:
        user: Union[User, None] = data.get('event_from_user')
        if not user:
            return await handler(event, data)
        session: AsyncSession = data['session']
        stmt = select(User.user_id).where(User.is_baned==True, User.user_id==data['event_from_user'].id)
        result = await session.execute(stmt)
        find_baned_user: int = result.first()
        if find_baned_user is not None:
            if event.event_type == 'callback_query':
                return await event.callback_query.answer()
            return
        return await handler(event, data)