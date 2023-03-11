from .schemas import WGUserModel, DBUserModel
from db.models import User
import subprocess



class UserModel(WGUserModel, DBUserModel):

    _bites_in = 2**10
    _meashures = {'B': 1, 'KB' : _bites_in,'MB' : _bites_in **2, 'GB': _bites_in **3, 'TB': _bites_in **4}

    def __str__(self) -> str:
        send = self._convert_from_bytes(self.send)
        received = self._convert_from_bytes(self.received)
        keys_ru = ('Имя', 'Локальный адрес', 'Статус', 'Внешний адрес/порт', 'Появлялся', 'Трафик')
        values = (
            self.user_name, 
            str(self.ip), 
            'заблокирован' if self.is_baned else 'активен', 
            self.endpoint, 
            self._time_data_prepare(), 
            f"{send} загружено, {received} отправлено")
        result = '\n'.join(map(lambda x: f"<b>{x[0]}:</b> <code>{x[1]}</code>", zip(keys_ru, values)))
        return result
    
    def _time_data_prepare(self):
        if isinstance(self.latest_handshake, str):
            return self.latest_handshake
        return self.latest_handshake.strftime("%H:%M:%S %d.%m.%Y")

    def _convert_from_bytes(self, value: int) -> float:
        for meashure in self._meashures.keys():
            res = round(value / self._meashures.get(meashure), 2)
            if res < 1000:
                return f"{res} {meashure}"

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
            user_statistics_list.append(UserModel(**peer.dict(), **DBUserModel.from_orm(db_user).dict()))
        else: 
            user_statistics_list.append(UserModel(**DBUserModel.from_orm(db_user).dict()))
    user_statistics_list = sorted(user_statistics_list, key=lambda x: x.received, reverse=True)
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