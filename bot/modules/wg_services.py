from .schemas import WGUserModel, DBUserModel
from db.models import User
import subprocess



class UserModel(WGUserModel, DBUserModel):
    def __str__(self) -> str:
        result = '\n'.join(map(
            lambda x: f"<b>{x[0]}:</b> <code>{x[1]}</code>", 
            zip(('Имя', 'Локальный адрес', 'Статус', 'Внешний адрес/порт', 'Появлялся', 'Трафик'),
                (   self.user_name, 
                    str(self.ip), 
                    'заблокирован' if self.is_baned else 'активен', 
                    self.endpoint, 
                    self.latest_handshake.strftime("%H:%M:%S %d.%m.%Y") if self.latest_handshake else 'нет данных',
                    _prepare_trafic_data(self.send, self.received)))))
        return result

async def data_preparation(data_db: list[User]) -> str:
    """Собирает вместе данные из БД и консоли Wireguard и перегоняет в удобный вид

    Args:
        data_db (List[User]): список объектов пользователей из БД

    Returns:
        str: подготовленная для вывода строка со статистикой пользователей
    """
    data_cmd: dict[str: WGUserModel] = await _check_statistics()
    user_statistics_list = []
    for db_user in data_db:
        peer: WGUserModel = data_cmd.get(db_user.pub_key)
        if peer and peer.endpoint != '(none)':
            user_statistics_list.append(UserModel(
                **peer.dict(), 
                **DBUserModel.from_orm(db_user).dict()))
        else: 
            user_statistics_list.append(UserModel(**DBUserModel.from_orm(db_user).dict()))
    return f"\n{'_'*32}\n".join(map(str, user_statistics_list))

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

async def _check_statistics() -> list[WGUserModel]:
    """Выполняет команду "wg show" и парсит вывод о каждом пользователе в словарь

    Returns:
        List[Dict]: данные об использовании страфика 
    """
    data = map(str.split, subprocess.getoutput('wg show all dump').split('\n')[1:])
    keys = ("peer","endpoint", "latest_handshake", "received", "send")
    return {i[1]: WGUserModel.parse_obj(dict(zip(keys, i[1:2] + i[3:4] + i[5:8]))) for i in data}

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