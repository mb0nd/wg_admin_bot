from typing import  Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from sqlalchemy.orm import sessionmaker
from db import create_async_engine, get_session_maker
import os



"""async def get_user_by_id(session: AsyncSession, user_id: int):
    user = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    return user"""

async def create_user(user_data: Dict, session_maker):
    async with session_maker() as session:
        session: AsyncSession
        async with session.begin():
            user = User(
                user_id = user_data['id'],
                user_name = user_data['name'],
                pub_key = user_data['pub_key'],
                ip = user_data['ip']
            )
        session.add(user)
        #await session.merge(user)
        await session.commit()
         