from typing import List, Dict, Union
from db.models import User
import subprocess
import os


class WgServices:

    @staticmethod
    async def check_statistics() -> List[Dict]:
        """Выполняет команду "wg show" и парсит вывод о каждом пользователе в словарь

        Returns:
            List[Dict]: данные об использовании страфика 
        """
        def str_to_dict(s: str):
            s.strip()
            if not s:
                return
            k,v = s.split(': ')
            return (k.strip(), v)
        output = subprocess.check_output(['wg', 'show']).decode('utf-8').splitlines()[5:]
        peers = list()
        peer = dict()
        for s in map(str_to_dict, output):
            if s is None:
                peers.append(peer)
                peer = dict()
                continue
            peer[s[0]] = s[1]
        else:
            peers.append(peer)
        return peers  

    @staticmethod
    async def data_preparation(data_db: Union[list, User]) -> str:
        """Собирает вместе данные из БД и консоли Wireguard и перегоняет в удобный вид

        Args:
            data_db (Union[list, User]): список объектов пользователей из БД

        Returns:
            str: подготовленная для вывода строка со статистикой пользователей
        """
        data_cmd = await WgServices.check_statistics()
        res=''
        for peer in data_cmd:
            for user in data_db:
                if peer.get('peer') == user.pub_key:
                    if peer.get('endpoint'):
                        res += f"<b>Имя:</b> <code>{user.user_name}</code>\n<b>Локальный адрес:</b> <code>{user.ip}</code>\n<b>Активен:</b> <code>{'нет' if user.is_baned else 'да'}</code>\n<b>Внешний адрес/порт</b>: <code>{peer['endpoint']}</code>\n<b>Появлялся:</b> <code>{peer['latest handshake']}</code>\n<b>Трафик:</b> <code>{peer['transfer']}</code>\n{'_'*50}\n"
                    else:
                        res += f"<b>Имя:</b> <code>{user.user_name}</code>\n<b>Локальный адрес:</b> <code>{user.ip}</code>\n<b>Активен:</b> <code>{'нет' if user.is_baned else 'да'}</code>\n{'_'*50}\n"
                    break
        if not res:
            return 'Не возможно отобразить статистику, пользователь(и) не найден в wireguard'
        return res

    @staticmethod
    async def restart_wg() -> tuple:
        """Выполняет команду перезапуска сервера Wireguard
        и проверяет статус после

        Returns:
            tuple: строка ответа админу и статус выполненеия
        """
        os.system('systemctl restart wg-quick@wg0')
        try:
            output = subprocess.check_output(['systemctl', 'status', 'wg-quick@wg0']).decode('utf-8').splitlines()[2]
            if 'Active: active' in output:
                return ("Сервер перезапущен", True)
            else:
                return (f"Что то пошло не так <code>{output}</code>", False)
        except subprocess.CalledProcessError:
            return (f"Что то пошло не так", False)