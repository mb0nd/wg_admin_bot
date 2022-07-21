from contextlib import suppress
from typing import  Dict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User


async def get_user_by_id(session: AsyncSession, user_id: int):
    user = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    return user

async def create_user(session: AsyncSession, user_data: Dict):
    entry = User()
    entry.user_id = user_data['user_id']
    entry.user_name = user_data['user_name']
    entry.full_name = user_data['full_name']
    #entry.pub_key = user_data['pub_key']
    #entry.ip = user_data['ip']
    session.add(entry)
    with suppress(IntegrityError):
        await session.commit()                   