from typing import  Dict, List
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from modules.user_callback import UserCallbackData
from modules.wg_user import WgUser
from db.models import User


async def create_user(user_data: Dict, session: AsyncSession) -> None:
    """Создание записи о новом пользователе в БД

    Args:
        user_data (Dict): словарь с данными о пользователе
        session (AsyncSession): сессия с БД
    """
    user = User(
        user_id = user_data['id'],
        user_name = user_data['name'],
        pub_key = user_data['pub_key'],
        ip = user_data['ip']
    )
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

async def delete_user_by_id(id: int, session: AsyncSession) -> None:
    """Удаление пользователя из БД

    Args:
        id (int): id пользователя
        session (AsyncSession): сессия с БД
    """
    stmt = delete(User).where(User.user_id == id)
    await session.execute(stmt)
    await session.commit()
        
async def switch_user_ban_status(callback_data: UserCallbackData, session: AsyncSession) -> None:
    """Изменить статус пользователя в БД (забанен / разбанен) 
       в зависимости от текущего состояние меняется на противоположное

    Args:
        callback_data (UserCallbackData): данные о пользователе
        session (AsyncSession): сессия с БД
        path_to_wg (str): путь к папке с wireguard
    """
    stmt = select(User.pub_key, User.ip, User.is_baned).where(User.user_id==callback_data.id)
    result = await session.execute(stmt)
    pub_key, ip, ban_status = result.first()
    await WgUser.switch_user_blocked_status(ip, pub_key, ban_status)
    stmt = update(User).where(User.user_id==callback_data.id).values(is_baned=not ban_status, updated_at=datetime.now())
    await session.execute(stmt)
    await session.commit()

async def switch_user_pay_status(callback_data: UserCallbackData, session: AsyncSession) -> None:
    """Изменить статус пользователя в БД (платный / бесплатный) 
       в зависимости от текущего состояние меняется на противоположное

    Args:
        callback_data (UserCallbackData): данные о пользователе
        session (AsyncSession): сессия с БД
    """
    stmt = select(User.is_pay).where(User.user_id==callback_data.id)
    result = await session.execute(stmt)
    pay_status = result.scalar()
    stmt = update(User).where(User.user_id==callback_data.id).values(is_pay=not pay_status, updated_at=datetime.now())
    await session.execute(stmt)
    await session.commit()

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