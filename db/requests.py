from typing import  Dict, List
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from user_callback import UserCallbackData
from gen_user import blocked_user, unblocked_user
from .models import User


async def create_user(user_data: Dict, session: AsyncSession) -> None:
    user = User(
        user_id = user_data['id'],
        user_name = user_data['name'],
        pub_key = user_data['pub_key'],
        ip = user_data['ip']
    )
    session.add(user)
    await session.commit()

async def delete_user_by_id(id: int, session: AsyncSession) -> None:
    stmt = delete(User).where(User.user_id == id)
    await session.execute(stmt)
    await session.commit()

async def ban_user(callback_data: UserCallbackData, session: AsyncSession, path_to_wg: str) -> None:
    stmt = select(User.pub_key).where(User.is_baned==False, User.user_id==callback_data.id)
    result = await session.execute(stmt)
    user_pub_key = result.scalar()
    if user_pub_key:
        await blocked_user(user_pub_key, path_to_wg)
        stmt = update(User).where(User.user_id==callback_data.id).values(is_baned=True, updated_at=datetime.now())
        await session.execute(stmt)
        await session.commit()
    else:
        user = User(
            user_id = callback_data.id,
            user_name = callback_data.name,
            is_baned = True
        )
        session.add(user)
        await session.commit()
        
async def uban_user(callback_data: UserCallbackData, session: AsyncSession, path_to_wg: str) -> None:
    stmt = select(User.pub_key, User.ip).where(User.is_baned==True, User.user_id==callback_data.id)
    result = await session.execute(stmt)
    pub_key, ip = result.first()
    if pub_key:
        await unblocked_user(pub_key, ip, path_to_wg)
        stmt = update(User).where(User.user_id==callback_data.id).values(is_baned=False, updated_at=datetime.now())
        await session.execute(stmt)
        await session.commit()

async def check_user_by_id(id: int, session: AsyncSession) -> int:
    stmt = select(User.user_id).where(User.user_id == id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    return user

async def get_user_by_id(id: int, session: AsyncSession) -> User:
    stmt = select(User).where(User.user_id == id)
    result = await session.execute(stmt)
    user = result.first()
    return user

async def get_blocked_users(session: AsyncSession) -> List[User]:
    stmt = select(User.user_id, User.user_name).where(User.is_baned==True, User.pub_key=="0", User.ip=="0")
    result = await session.execute(stmt)
    blocked_users = result.all()
    return blocked_users

async def get_real_users(session: AsyncSession) -> List[User]:
    stmt = select(User).where(User.pub_key!="0", User.ip!="0")
    result = await session.execute(stmt)
    real_users = result.scalars().all()
    return real_users

async def get_pay_users(session: AsyncSession) -> List[int]:
    stmt = select(User.user_id).where(User.is_pay == True)
    result = await session.execute(stmt)
    pay_users = result.scalars().all()
    return pay_users