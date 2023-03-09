from typing import Dict, List
#from .schemas import Peer
from db.models import User
import subprocess
import datetime

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
                'Появлялся': 'нет данных',
                'Трафик': 'нет данных'}
        peer: dict = data_cmd.get(user.pub_key)
        if peer and peer.get('latest_handshake'):
            user_statistic['Внешний адрес/порт'] = peer['endpoint']
            #user_statistic['Появлялся'] = _prepare_time_data(peer['latest handshake'])
            user_statistic['Появлялся'] = peer['latest_handshake'].strftime("%H:%M:%S %d.%m.%Y")
            user_statistic['Трафик'] = _prepare_trafic_data(peer['send'], peer['received'])
        user_statistics_list.append(user_statistic)
    # Тут можно делать сортировки
    #user_statistics_list = sorted(
    #    user_statistics_list, 
    #    key=lambda x: _convert_to_bytes(*x['Трафик'].split()[:2]),
    #    reverse=True)
    for user in user_statistics_list:
        result +="\n".join(map(lambda x: f"<b>{x[0]}:</b> <code>{x[1]}</code>", user.items())) + f"\n{'_'*32}\n"
    return result

async def new_data_preparation(data_db: List[User]) -> str:
    data_cmd = await _check_statistics()

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
    data = map(str.split, subprocess.getoutput('wg show all dump').split('\n')[1:])
    keys = ("endpoint", "allowed_ips", "latest_handshake", "received", "send")
    return {i[1]: dict(zip(keys, i[3:8])) for i in data}


def _prepare_time_data(time_string: str) -> str:
    """Подготавливает строку с датой и временем к нужному виду,
    которая показывает когда клиент подключался последний раз

    Returns:
        str: строка формата '19:12:32 12.01.2023'
    """
    prepare_data = list(map(lambda x: int(x.split()[0]), time_string.split(', ')))
    prepare_data.reverse()
    prepare_data = dict(zip(('seconds', 'minutes', 'hours', 'days'), prepare_data))
    result: datetime.datetime = datetime.datetime.now() - datetime.timedelta(**prepare_data)
    return result.strftime("%H:%M:%S %d.%m.%Y")

def _get_units() -> dict:
    """Возвращает словарь с приставками единиц измерения данных и значением множителя
    """
    bites_in = 2**10
    return {'B': 1, 'KiB' : bites_in,'MiB' : bites_in **2, 'GiB': bites_in **3, 'TB': bites_in **4}

def _convert_from_bytes(value: int) -> float:
    """Конвертирует полученное значение value из полученной
    единицы измерения measure в байты
    Returns:
        float: значение в байтах
    """
    meashures = _get_units()
    for meashure in meashures.keys():
        res =  value / meashures.get(meashure)
        if res < 1000:
            return f"{res} {meashure}"

def _prepare_trafic_data(send: int, received: int) -> str:
    """Получает строку в формате '10.63 KiB received, 8.34 KiB sent'
    Возвращает строку в формате '700.97 KiB загружено, 2.04 MiB отправлено'
    Понятия загружено и отправлено поменяны местами т.к. изначальные данные 
    определены со стороны сервера, возвращаем мы их относительно клиента.
    """
    return f"{_convert_from_bytes(received)} загружено, {_convert_from_bytes(send)} отправлено"