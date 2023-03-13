from typing import List
from ipaddress import IPv4Address
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from cb_data import UserCallbackData
from db.models import DbUser


async def write_user_to_db(user: DbUser, session: AsyncSession) -> None:
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
    user = DbUser(
        user_id = callback_data.id,
        user_name = callback_data.name,
        is_baned = True,
        is_pay = False
    )
    session.add(user)

async def delete_user_in_db(user: DbUser, session: AsyncSession) -> None:
    """Удаление пользователя из БД

    Args:
        user (User): объект модели данных
        session (AsyncSession): сессия с БД
    """
    await session.delete(user)

async def get_blocked_users(session: AsyncSession) -> List[DbUser]:
    """Поллучить из БД всех пользователей которым доступ был отклонен и
       не генерировался конфиг

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        List[User]: список объектов класса User
    """
    stmt = select(DbUser.user_id, DbUser.user_name).where(DbUser.is_baned==True, DbUser.pub_key=="0", DbUser.ip=="0")
    result = await session.execute(stmt)
    blocked_users = result.all()
    return blocked_users

async def get_real_users(session: AsyncSession) -> List[DbUser]:
    """Получение списка всех пользователей из БД, которым разрешался доступ
       включая забаненых

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        List[User]: список объектов класса User
    """
    stmt = select(DbUser).where(DbUser.pub_key!="0", DbUser.ip!="0").order_by(DbUser.created_at)
    real_users = await session.scalars(stmt)
    return real_users

async def get_pay_users(session: AsyncSession) -> List[int]:
    """Получение из БД всех пользователей, которым разрешался доступ
       с пометкой о платной учетной записи

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        List[int]: список объектов класса User
    """
    stmt = select(DbUser.user_id).where(DbUser.is_pay == True)
    pay_users =  await session.scalars(stmt)
    return pay_users

async def get_next_ip(session: AsyncSession) -> str:
    """Возвращает следующий за максимальным ip адрес из БД

    Args:
        session (AsyncSession): сессия с БД

    Returns:
        str: ip 
    """
    result = await session.scalars(select(func.max(DbUser.ip)))
    ip = result.first()
    if ip is None:
        return '10.0.0.10'
    return str(IPv4Address(ip) + 1)