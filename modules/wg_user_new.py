from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import FSInputFile
from db.models import User
from modules.env_reader import env
from db.requests import get_next_ip, write_new_user
import subprocess
import os

class WgUser:

    path_to_wg = env.path_to_wg
    hostname = os.uname().nodename
    serverPublickey = subprocess.getoutput(f'cat {path_to_wg}publickey')

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
    

    def __init__(self, user: User) -> None:
        self.path_to_user = WgUser.path_to_wg + user.user_name
        self.name = user.user_name
        self.publickey = user.pub_key
        self.ip = user.ip
        self.privatekey = user.privatekey if 'privatekey' in user.__dict__ else None
        self.user_object = user

    async def set_new_peer(self) -> None:
        """
        Добавляет нового пользователя в текущий инстанс wireguard,
        и дописывает новый peer в wg0.conf
        """
        with open(f'{WgUser.path_to_wg}wg0.conf', 'a', encoding='utf-8') as file:
            file.write(f"\n[Peer]\nPublicKey = {self.publickey}\nAllowedIPs = {self.ip}/32")
        os.system( f"wg set wg0 peer {self.publickey} allowed-ips {self.ip}/32")
        
    async def generate_peer_config(self) -> None:
        """
        Создает конфигурационный файл пользователя,
        при отсутствии создает папку пользователя
        """
        content = f"[Interface]\nPrivateKey = {self.privatekey}\nAddress = {self.ip}/32\n"\
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {self.serverPublickey}\n"\
            f"Endpoint = {self.hostname}:{env.listen_port}\n"\
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        if not os.path.exists(self.path_to_user):
            os.mkdir(f"{self.path_to_user}")
        await WgUser.file_writer(f'{self.path_to_user}/{self.name}.conf', content)

    async def create_user(self, session: AsyncSession) -> FSInputFile:
        """Метод создает пользователя

        Args:
            session (AsyncSession): сессия с БД

        Returns:
            FSInputFile: конфигурационный файл
        """
        await self.set_new_peer()
        await self.generate_peer_config()
        del self.user_object.privatekey
        await write_new_user(self.user_object, session) # Пока так... надо подумать
        config = FSInputFile(f'{self.path_to_user}/{self.name}.conf', filename=f'{self.name}.conf')
        return config


async def get_user(id: int, name: str, session: AsyncSession) -> WgUser:
        """Метод получает пользователя из БД, 
        - если находит то отдает полученые данные в конструктор класса и возвращает экземпляр
        - если нет то собирает данные из файлов и вывода и передает в конструктор,
        также возвращаа экземпляр класса

        Args:
            id (int): id пользователя из Telegram

        Returns:
            WgUser: экземпляр класса
        """
        user = await session.get(User, id)
        if user is None:
            privatekey = subprocess.getoutput('wg genkey')
            user = User()
            user.user_id = id
            user.user_name = name
            user.pub_key = subprocess.getoutput(f'echo {privatekey} | wg pubkey')
            user.ip = await get_next_ip(session)
            #session.add(user)
            #await session.commit()     Можно писать пользователя в базу прямо тут, но х3 как обернется дальше
            user.privatekey = privatekey
        return WgUser(user)


        ##subprocess.run(['wg', 'set', 'wg0', 'peer', self.publickey, 'allowed-ips', f'{self.ip}/32'])
