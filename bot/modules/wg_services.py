from typing import Dict, Union
from db.models import User
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

async def check_statistics() -> Dict:
    """Выполняет команду "wg show" и парсит вывод о каждом пользователе в словарь

    Returns:
        List[Dict]: данные об использовании страфика 
    """
    output = (x.strip().split(': ') for x in subprocess.getoutput('wg show').splitlines()[5:] if x)
    result = {}
    for k, v in output:
        if k == 'peer':
            key = v
            result[key] = {}
        else:
            result[key][k] = v
    return result
    
async def data_preparation(data_db: Union[list, User]) -> str:
    """Собирает вместе данные из БД и консоли Wireguard и перегоняет в удобный вид

    Args:
        data_db (Union[list, User]): список объектов пользователей из БД

    Returns:
        str: подготовленная для вывода строка со статистикой пользователей
    """
    data_cmd = await check_statistics()
    res=''
    for user in data_db:
        peer: dict = data_cmd.get(user.pub_key)
        if peer and peer.get('endpoint'):
            res += f"<b>Имя:</b> <code>{user.user_name}</code>\n<b>Локальный адрес:</b> <code>{user.ip}</code>\n<b>Активен:</b> <code>{'нет' if user.is_baned else 'да'}</code>\n<b>Внешний адрес/порт</b>: <code>{peer['endpoint']}</code>\n<b>Появлялся:</b> <code>{peer['latest handshake']}</code>\n<b>Трафик:</b> <code>{peer['transfer']}</code>\n{'_'*50}\n"
        else:
            res += f"<b>Имя:</b> <code>{user.user_name}</code>\n<b>Локальный адрес:</b> <code>{user.ip}</code>\n<b>Активен:</b> <code>{'нет' if user.is_baned else 'да'}</code>\n{'_'*50}\n"
    if not res:
        return 'Не возможно отобразить статистику, пользователь(и) не найден в wireguard'
    return res

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