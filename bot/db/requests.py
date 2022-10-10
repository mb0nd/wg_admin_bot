from typing import List
from ipaddress import IPv4Address
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from cb_data import UserCallbackData
from db.models import User


async def write_user_to_db(user: User, session: AsyncSession) -> None:
    """Записать данные пользователя в БД

    Args:
        user (User): объект модели данных
        session (AsyncSession): сессия с БД
    """
    session.add(user)

async def decline_access_user(callback_data: UserCallbackData, session: AsyncSession) -> None:
    """Записать в БД данные о пользователе, которому доступ отклонен (теневой бан)

    Args:
        callback_data (UserCallbackData): данные о пользователе
        session (AsyncSession): сессия с БД
    """
    user = User(
        user_id = callback_data.id,
        user_name = callback_data.name,
        is_baned = True,
        is_pay = False
    )
    session.add(user)

async def delete_user_in_db(user: User, session: AsyncSession) -> None:
    """Удаление пользователя из БД

    Args:
        user (User): объект модели данных
        session (AsyncSession): сессия с БД
    """
    await session.delete(user)

async def get_blocked_users(session: AsyncSession) -> List[User]:
    """Поллучить из БД всех пользователей которым доступ был отклонен и
       не генерировался конфиг

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        List[User]: список объектов класса User
    """
    stmt = select(User.user_id, User.user_name).where(User.is_baned==True, User.pub_key=="0", User.ip=="0")
    result = await session.execute(stmt)
    blocked_users = result.all()
    return blocked_users

async def get_real_users(session: AsyncSession) -> List[User]:
    """Получение списка всех пользователей из БД, которым разрешался доступ
       включая забаненых

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        List[User]: список объектов класса User
    """
    stmt = select(User).where(User.pub_key!="0", User.ip!="0")
    result = await session.execute(stmt)
    real_users = result.scalars().all()
    return real_users

async def get_pay_users(session: AsyncSession) -> List[int]:
    """Получение из БД всех пользователей, которым разрешался доступ
       с пометкой о платной учетной записи

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        List[int]: список объектов класса User
    """
    stmt = select(User.user_id).where(User.is_pay == True)
    result = await session.execute(stmt)
    pay_users = result.scalars().all()
    return pay_users

async def get_next_ip(session: AsyncSession) -> str:
    """Возвращает следующий за максимальным ip адрес из БД

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        str: ip 
    """
    result = await session.scalars(select(func.max(User.ip)))
    ip = result.first()
    if ip is None:
        return '10.0.0.10'
    return str(IPv4Address(ip) + 1)