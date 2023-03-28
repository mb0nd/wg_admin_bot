from sqlalchemy.ext.asyncio import AsyncSession
from modules.wg_user import WgUser
from asyncio import sleep
from datetime import datetime, timedelta
from db.models import DbUser
from modules.schemas import WGUserModel
from db.requests import get_next_ip, write_user_to_db
import subprocess


def check_username(name: str) -> bool:
    """Проверяет введенное имя пользователя на соответствие правилам

    Args:
        name (str): имя введенное пользователем

    Returns:
        bool: прошло / не прошло проверку
    """
    if isinstance(name, str) and 3 < len(name) < 12 and name[0].isalpha():
        return True
    return False

async def get_user(id: int, session: AsyncSession, name: str = None) -> WgUser:
        """Метод получает пользователя из БД, 
        - если находит то отдает полученые данные в конструктор класса и возвращает экземпляр
        - если нет то собирает данные из файлов и вывода и передает в конструктор,
        также возвращаа экземпляр класса

        Args:
            id (int): id пользователя из Telegram

        Returns:
            WgUser: экземпляр класса
        """
        user = await session.get(DbUser, id)
        if user is None:
            privatekey = subprocess.getoutput('wg genkey')
            user = DbUser(
                user_id = id,
                user_name = name,
                pub_key = subprocess.getoutput(f'echo {privatekey} | wg pubkey'),
                ip = await get_next_ip(session)
            )
            await write_user_to_db(user, session)
            await session.commit()
            user.privatekey = privatekey
        return WgUser(user_object = user, wg_user_model = await check_statistics(user.pub_key))

async def check_statistics(pub_key: str | None = None) -> list[WGUserModel] | WGUserModel:
        """Выполняет команду "wg show" и парсит вывод о каждом пользователе в словарь

        Returns:
            List[Dict]: данные об использовании страфика 
        """
        data = filter(lambda x: x[3] != '(none)', map(str.split, subprocess.getoutput('wg show all dump').split('\n')[1:]))
        keys = ("endpoint", "latest_handshake", "received", "send")
        result = {i[1]: WGUserModel.parse_obj(dict(zip(keys, i[3:4] + i[5:8]))) for i in data}
        if pub_key is None:
            return result
        if pub_key in result:
            return result.get(pub_key)
        return WGUserModel()

async def check_first_connection(pub_key: str) -> bool:
    start = datetime.utcnow()
    while datetime.utcnow() < start + timedelta(minutes=30):
        user: WGUserModel = await check_statistics(pub_key)
        if user.endpoint != 'нет данных':
            return True
        else:
            await sleep(30)
    return False

async def restart_wg() -> tuple:
    """Выполняет команду перезапуска сервера Wireguard
    и проверяет статус после

    Returns:
        tuple: строка ответа админу и статус выполненеия
    """
    try:
        output = subprocess.getstatusoutput('wg-quick down wg0 && wg-quick up wg0')
        if output[0] == 0:
            return (f'Сервер перезапущен', True)
        else:
            return (f'<code>{output[1]}</code>', False)
    except subprocess.CalledProcessError:
        return (f"Что то пошло не так", False)
    
async def data_preparation(data_db: list[DbUser]) -> str:
    """Собирает вместе данные из БД и консоли Wireguard и перегоняет в удобный вид

    Args:
        data_db (List[User]): список объектов пользователей из БД

    Returns:
        str: подготовленная для вывода строка со статистикой пользователей
    """
    data_cmd: dict[str: WGUserModel] = await check_statistics()
    user_statistics_list = []
    for db_user in data_db:
        peer: WGUserModel = data_cmd.get(db_user.pub_key)
        if peer:
            user_statistics_list.append(WgUser(user_object = db_user, wg_user_model=peer))
        else: 
            user_statistics_list.append(WgUser(user_object = db_user, wg_user_model=WGUserModel()))
    user_statistics_list = sorted(user_statistics_list, key=lambda x: x.wg_user_model.send, reverse=True)
    return f"\n{'_'*32}\n".join(map(str, user_statistics_list))