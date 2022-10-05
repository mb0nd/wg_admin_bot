from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import FSInputFile
from datetime import datetime
from db.models import User
from modules.env_reader import env
from db.requests import get_next_ip, write_user_to_db, delete_user_in_db
import subprocess
import os

class WgUser:

    path_to_wg = env.path_to_wg
    path_to_user_configs = path_to_wg + 'user_configs'
    serverPublickey = subprocess.getoutput(f'cat {path_to_wg}publickey')

    @staticmethod
    async def __file_reader(path_to_file: str) -> str:
        """Интерфейс для чтения файлов

        Args:
            path_to_file (str): путь к файлу

        Returns:
            str: содержимое файла
        """
        with open(f'{path_to_file}', 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    async def __file_writer(path_to_file: str, content: str) -> None:
        """Интерфейс для записи файлов

        Args:
            path_to_file (str): путь к файлу
            content (str): данные для записи
        """
        with open(f'{path_to_file}', 'w', encoding='utf-8') as file:
            file.write(content)
    
    def __init__(self, user: User) -> None:
        self.user_object = user

    async def __set_new_peer(self) -> None:
        """
        Добавляет нового пользователя в текущий инстанс wireguard,
        и дописывает новый peer в wg0.conf
        """
        with open(f'{WgUser.path_to_wg}wg0.conf', 'a', encoding='utf-8') as file:
            file.write(f"\n[Peer]\nPublicKey = {self.user_object.pub_key}\nAllowedIPs = {self.user_object.ip}/32")
        os.system( f"wg set wg0 peer {self.user_object.pub_key} allowed-ips {self.user_object.ip}/32")
        
    async def __generate_peer_config(self) -> None:
        """
        Создает конфигурационный файл пользователя,
        при отсутствии создает папку пользователя
        """
        content = f"[Interface]\nPrivateKey = {self.user_object.privatekey}\nAddress = {self.user_object.ip}/32\n"\
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {self.serverPublickey}\n"\
            f"Endpoint = {env.host}:{env.listen_port}\n"\
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        if not os.path.exists(self.path_to_user_configs):
            os.mkdir(self.path_to_user_configs)
        await self.__file_writer(f'{self.path_to_user_configs}/{self.user_object.user_name}.conf', content)

    async def create_user(self) -> FSInputFile:
        """Метод создает пользователя

        Args:
            session (AsyncSession): сессия с БД

        Returns:
            FSInputFile: конфигурационный файл
        """
        await self.__set_new_peer()
        await self.__generate_peer_config()
        config = FSInputFile(f'{self.path_to_user_configs}/{self.user_object.user_name}.conf', filename=f'{self.user_object.user_name}.conf')
        return config

    async def switch_ban_status(self, session: AsyncSession) -> None:
        input_text = await self.__file_reader(f"{self.path_to_wg}wg0.conf")
        if not self.user_object.is_baned:
            os.system(f'wg set wg0 peer {self.user_object.pub_key} remove')
            output_text = input_text.replace(self.user_object.pub_key, f"%BANNED%{self.user_object.pub_key}")
        else:
            os.system(f'wg set wg0 peer {self.user_object.pub_key} allowed-ips {self.user_object.ip}/32')
            output_text = input_text.replace(f"%BANNED%{self.user_object.pub_key}", self.user_object.pub_key)
        await self.__file_writer(f"{self.path_to_wg}wg0.conf", output_text)
        self.user_object.is_baned = not self.user_object.is_baned
        self.user_object.updated_at = datetime.now()
        await write_user_to_db(self.user_object, session)

    async def switch_pay_status(self, session: AsyncSession) -> None:
        self.user_object.is_pay = not self.user_object.is_pay
        self.user_object.updated_at = datetime.now()
        await write_user_to_db(self.user_object, session)

    async def delete_user(self, session: AsyncSession) -> None:
        """Удаляет данные о пользователе из wireguard, включая файлы и папки

        Args:
            user (User): объект класса модели пользователя
        """
        os.system(f'wg set wg0 peer {self.user_object.pub_key} remove')
        with open(f'{self.path_to_wg}wg0.conf', 'r', encoding='utf-8') as f:
            input_text = f.readlines()
        for i in range(len(input_text)):
            if self.user_object.pub_key in input_text[i]:
                for _ in range(3):
                    input_text.pop(i-1)
                break
        input_text[-1] = input_text[-1].rstrip()
        with open(f'{self.path_to_wg}wg0.conf', 'w', encoding='utf-8') as f:
            f.writelines(input_text)
        os.remove(f'{self.path_to_user_configs}/{self.user_object.user_name}.conf')
        await delete_user_in_db(self.user_object, session)

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
        user = await session.get(User, id)
        if user is None:
            privatekey = subprocess.getoutput('wg genkey')
            user = User(
                user_id = id,
                user_name = name,
                pub_key = subprocess.getoutput(f'echo {privatekey} | wg pubkey'),
                ip = await get_next_ip(session)
            )
            await write_user_to_db(user, session)
            user.privatekey = privatekey
        return WgUser(user)