from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User



class IsBanedMiddleware(BaseMiddleware):

    def __init__(self, session_maker):
        super().__init__()
        self.session_maker = session_maker
    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], 
        event: Update, 
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            session: AsyncSession
            stmt = select(User).where(User.is_baned==True, User.user_id==data['event_from_user'].id)
            result = await session.execute(stmt)
            find_baned_user: User = result.first()
            print(find_baned_user)
        if find_baned_user is not None:
            if event.event_type is 'callback_query':
                return await event.callback_query.answer()
            return
        return await handler(event, data)