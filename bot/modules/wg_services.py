from typing import Dict, List
from db.models import User
import subprocess
import datetime

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

async def data_preparation(data_db: List[User]) -> str:
    """Собирает вместе данные из БД и консоли Wireguard и перегоняет в удобный вид

    Args:
        data_db (List[User]): список объектов пользователей из БД

    Returns:
        str: подготовленная для вывода строка со статистикой пользователей
    """
    result = '' 
    user_statistics_list = []
    data_cmd = await _check_statistics()
    for user in data_db:
        user_statistic = {
                'Имя': user.user_name,
                'Локальный адрес': user.ip,
                'Статус': 'заблокирован' if user.is_baned else 'активен',
                'Внешний адрес/порт': 'нет данных',
                'Появлялся:': 'нет данных',
                'Трафик': 'нет данных'}
        peer: dict = data_cmd.get(user.pub_key)
        if peer and peer.get('endpoint'):
            user_statistic['Внешний адрес/порт'] = peer['endpoint']
            user_statistic['Появлялся:'] = _prepare_time_data(peer['latest handshake'])
            user_statistic['Трафик'] = peer['transfer']
        user_statistics_list.append(user_statistic)
    # Тут можно делать сортировки
    user_statistics_list = sorted(
        user_statistics_list, 
        key=lambda x: _convert_to_bytes(*x['Трафик'].split()[:2]),
        reverse=True)
    for user in user_statistics_list:
        result +="\n".join(map(lambda x: f"<b>{x[0]}:</b> <code>{x[1]}</code>", user.items())) + f"\n{'_'*32}\n"
    return result

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

async def _check_statistics() -> Dict:
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

def _prepare_time_data(time_string: str) -> str:
    """Подготавливает строку с датой и временем к нужному виду,
    которая показывает когда клиент подключался последний раз

    Returns:
        str: строка формата '19:12:32 12.01.2023'
    """
    def _get_timedelta(seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0) -> datetime:
        """Вычисляет разницу во времени вычитая прошедшее с последнего подключения
        из текущего
        """
        delta = datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)
        return datetime.datetime.now() - delta
    prepare_data = list(map(lambda x: int(x.split()[0]), time_string.split(', ')))
    prepare_data.reverse()
    result: datetime.datetime = _get_timedelta(*prepare_data)
    return result.strftime("%H:%M:%S %d.%m.%Y")

def _get_units() -> dict:
    bites_in = 2**10
    return {'KiB' : bites_in,'MiB' : bites_in **2, 'GiB': bites_in **3}

def _convert_to_bytes(value: str, measure: str) -> float:
    try:
        return float(value) * _get_units()[measure]
    except (ValueError, KeyError):
        return 0