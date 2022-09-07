from typing import Tuple
from aiogram.types import FSInputFile
from db.models import User
from modules.env_reader import env
import os
import subprocess

class WgUser:
    """
    Класс предназначен для создания удаления и редактирования конфигурационных файлов wireguard
    в частности для работы с пользователями.
    """
    path_to_wg = env.path_to_wg
    hostname = os.uname().nodename
    serverPublickey = subprocess.getoutput(f'cat {path_to_wg}publickey')

    def __init__(self, name: str) -> None:
        self.path_to_user = WgUser.path_to_wg + name
        self.name = name
        self.privatekey = subprocess.getoutput('wg genkey')
        self.publickey = subprocess.getoutput(f'echo {self.privatekey} | wg pubkey')

    @staticmethod
    async def file_reader(path_to_file: str) -> str:
        """Интерфейс для чтения файлов

        Args:
            path_to_file (str): путь к файлу

        Returns:
            str: содержимое файла
        """
        with open(f'{path_to_file}', 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    async def file_writer(path_to_file: str, content: str) -> None:
        """Интерфейс для записи файлов

        Args:
            path_to_file (str): путь к файлу
            content (str): данные для записи
        """
        with open(f'{path_to_file}', 'w', encoding='utf-8') as file:
            file.write(content)

    @classmethod
    async def switch_user_blocked_status(cls, current_ip: str, publickey: str, status: bool) -> None:
        """Блокирует / разблокирует пользователя

        Args:
            current_ip (str): ip пользователя
            publickey (str): публичный ключ пользователя
            status (bool): текущий статус (забенен / разбанен)
        """
        input_text = await WgUser.file_reader(f"{WgUser.path_to_wg}wg0.conf")
        if not status:
            os.system(f'wg set wg0 peer {publickey} remove')
            output_text = input_text.replace(publickey, f"%BANNED%{publickey}")
        else:
            os.system(f'wg set wg0 peer {publickey} allowed-ips {current_ip}/32')
            output_text = input_text.replace(f"%BANNED%{publickey}", publickey)
        await WgUser.file_writer(f"{WgUser.path_to_wg}wg0.conf", output_text)
    
    @classmethod
    async def remove_user(cls, user: User) -> None:
        """Удаляет данные о пользователе из wireguard, включая файлы и папки

        Args:
            user (User): объект класса модели пользователя
        """
        os.system(f'wg set wg0 peer {user.pub_key} remove')
        with open(f'{WgUser.path_to_wg}wg0.conf', 'r', encoding='utf-8') as f:
            input_text = f.readlines()
        for i in range(len(input_text)):
            if user.pub_key in input_text[i]:
                for _ in range(3):
                    input_text.pop(i-1)
                break
        input_text[-1] = input_text[-1].rstrip()
        with open(f'{WgUser.path_to_wg}wg0.conf', 'w', encoding='utf-8') as f:
            f.writelines(input_text)
        os.system(f'rm -rf {WgUser.path_to_wg}{user.user_name}')

    async def get_next_ip(self) -> None:
        """
        Читает последний использованный ip из файла,
        добавляет +1 к последнему октету для использования 
        в экземпляре класса.
        """
        ip = await self.file_reader("last_ip")
        ip = ip.strip().split('.')
        ip[-1] = str(int(ip[-1])+1)
        self.current_ip = '.'.join(ip)

    async def set_new_peer(self) -> None:
        """
        Добавляет нового пользователя в текущий инстанс wireguard,
        и дописывает новый peer в wg0.conf
        """
        with open(f'{WgUser.path_to_wg}wg0.conf', 'a', encoding='utf-8') as file:
            file.write(f"\n[Peer]\nPublicKey = {self.publickey}\nAllowedIPs = {self.current_ip}/32")
        os.system ( f"wg set wg0 peer {self.publickey} allowed-ips {self.current_ip}/32")

    async def generate_peer_config(self) -> None:
        """
        Создает конфигурационный файл пользователя,
        при отсутствии создает папку пользователя
        """
        content = f"[Interface]\nPrivateKey = {self.privatekey}\nAddress = {self.current_ip}/32\n"\
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {self.serverPublickey}\n"\
            f"Endpoint = {self.hostname}:{env.listen_port}\n"\
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        if not os.path.exists(self.path_to_user):
            os.mkdir(f"{self.path_to_user}")
        await WgUser.file_writer(f'{self.path_to_user}/{self.name}.conf', content)

    async def add_user(self) -> Tuple:
        """Создает пользователя, используя смежные методы и отдает
        данные для записи в БД и отпрвки пользователю
        
        Returns:
            Tuple: публичный ключ, ip, конфигурационный файл
        """
        await self.get_next_ip()
        await self.set_new_peer()
        await self.generate_peer_config()
        await WgUser.file_writer('last_ip', self.current_ip)
        config = FSInputFile(f'{self.path_to_user}/{self.name}.conf', filename=f'{self.name}.conf')
        return (self.publickey, self.current_ip, config)