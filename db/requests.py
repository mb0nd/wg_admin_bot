from typing import  Dict, List
from datetime import datetime
from ipaddress import IPv4Address
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.user_callback import UserCallbackData
from modules.wg_user import WgUser
from db.models import User


async def write_user_to_db(user: User, session: AsyncSession) -> None:
    session.add(user)
    await session.commit()

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
    await session.commit()

async def delete_user_in_db(user: User, session: AsyncSession) -> None:
    """Удаление пользователя из БД

    Args:
        id (int): id пользователя
        session (AsyncSession): сессия с БД
    """
    #stmt = delete(User).where(User.user_id == id)
    await session.delete(user)
    await session.commit()
        
async def switch_user_ban_status(user: User, session: AsyncSession) -> None:
    stmt = update(User).where(User.user_id==user.user_id).values(is_baned = not user.is_baned, updated_at = datetime.now())
    await session.execute(stmt)
    await session.commit()

"""async def switch_user_pay_status(callback_data: UserCallbackData, session: AsyncSession) -> None:
    stmt = select(User.is_pay).where(User.user_id==callback_data.id)
    result = await session.execute(stmt)
    pay_status = result.scalar()
    stmt = update(User).where(User.user_id==callback_data.id).values(is_pay=not pay_status, updated_at=datetime.now())
    await session.execute(stmt)
    await session.commit()"""

async def check_user_by_id(id: int, session: AsyncSession) -> int:
    """Проверка на существование пользователя в БД по id

    Args:
        id (int): id пользователя
        session (AsyncSession): сессия с БД

    Returns:
        User: объект пользователя
    """
    stmt = select(User.user_id).where(User.user_id == id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    return user

async def get_user_by_id(id: int, session: AsyncSession) -> User:
    """Получение объекта пользователя из БД по id

    Args:
        id (int): id пользователя
        session (AsyncSession): сессия с БД

    Returns:
        User: объект пользователя
     """
    #вариант заменить на user = await session.get(User, id)
   
    stmt = select(User).where(User.user_id == id)
    result = await session.execute(stmt)
    user = result.first()
    return user

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
    return str(IPv4Address(ip) + 1)