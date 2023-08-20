from asyncio.log import logger
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import FSInputFile
from datetime import datetime, timedelta
from db.models import DbUser
from env_reader import Settings
from modules.schemas import WGUserModel
from db.requests import write_user_to_db, delete_user_in_db
import subprocess
import os




class WgUser:

    env = Settings()
    path_to_wg: str = env.path_to_wg
    path_to_user_configs: str = path_to_wg + 'user_configs'
    serverPublickey: str = subprocess.getoutput(f'cat {path_to_wg}publickey')

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
    
    async def delete_user(self, session: AsyncSession) -> None:
        """Удаляет данные о пользователе из wireguard, включая файлы и папки

        Args:
            user (User): объект класса модели пользователя
        """
        subprocess.run(['wg', 'set', 'wg0', 'peer', self.user_object.pub_key, 'remove'])
        try:
            input_text = await self.__file_reader(f'{self.path_to_wg}wg0.conf', lines=True)    
            for i in range(len(input_text)):
                if self.user_object.pub_key in input_text[i]:
                    for _ in range(3):
                        input_text.pop(i-1)
                    break
            input_text[-1] = input_text[-1].rstrip()
            await self.__file_writer(f'{self.path_to_wg}wg0.conf', input_text, lines=True)
            os.remove(f'{self.path_to_user_configs}/{self.user_object.user_name}.conf')
        except (FileNotFoundError, IndexError):
            logger.error("Файл /etc/wireguard/wg0.conf отсутстует или поврежден.")
        await delete_user_in_db(self.user_object, session)
        await session.commit()

    async def switch_ban_status(self, session: AsyncSession) -> None:
        input_text = await self.__file_reader(f"{self.path_to_wg}wg0.conf")
        if not self.user_object.is_baned:
            subprocess.run(['wg', 'set', 'wg0', 'peer', self.user_object.pub_key, 'remove'])
            output_text = input_text.replace(f"AllowedIPs = {self.user_object.ip}/32", f"#AllowedIPs = {self.user_object.ip}/32")
        else:
            subprocess.run(['wg', 'set', 'wg0', 'peer', self.user_object.pub_key, 'allowed-ips', self.user_object.ip + '/32'])
            output_text = input_text.replace(f"#AllowedIPs = {self.user_object.ip}/32", f"AllowedIPs = {self.user_object.ip}/32")
        await self.__file_writer(f"{self.path_to_wg}wg0.conf", output_text)
        self.user_object.is_baned = not self.user_object.is_baned
        self.user_object.updated_at = datetime.now()
        await write_user_to_db(self.user_object, session)
        await session.commit()

    async def switch_pay_status(self, session: AsyncSession) -> None:
        self.user_object.is_pay = not self.user_object.is_pay
        self.user_object.updated_at = datetime.now()
        await write_user_to_db(self.user_object, session)
        await session.commit()

    async def __set_new_peer(self) -> None:
        """
        Добавляет нового пользователя в текущий инстанс wireguard,
        и дописывает новый peer в wg0.conf
        """
        with open(f'{WgUser.path_to_wg}wg0.conf', 'a', encoding='utf-8') as file:
            file.write(f"\n[Peer]\nPublicKey = {self.user_object.pub_key}\nAllowedIPs = {self.user_object.ip}/32")
        subprocess.run(['wg', 'set', 'wg0', 'peer', self.user_object.pub_key, 'allowed-ips', self.user_object.ip + '/32'])
        
    async def __generate_peer_config(self) -> None:
        """
        Создает конфигурационный файл пользователя,
        при отсутствии создает папку пользователя
        """
        content = f"[Interface]\nPrivateKey = {self.user_object.privatekey}\nAddress = {self.user_object.ip}/32\n"\
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {self.serverPublickey}\n"\
            f"Endpoint = {self.env.host}:{self.env.listen_port}\n"\
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        if not os.path.exists(self.path_to_user_configs):
            os.mkdir(self.path_to_user_configs)
        await self.__file_writer(f'{self.path_to_user_configs}/{self.user_object.user_name}.conf', content)
    
    def __time_data_prepare(self):
        if isinstance(self.wg_user_model.latest_handshake, str):
            return self.wg_user_model.latest_handshake
        res = self.wg_user_model.latest_handshake + timedelta(hours=3)
        return res.strftime("%H:%M:%S %d.%m.%Y")

    def __convert_from_bytes(self, value: int) -> float:
        BITES_IN = 2**10
        MEASHURES = {'B': 1, 'KB' : BITES_IN,'MB' : BITES_IN **2, 'GB': BITES_IN **3, 'TB': BITES_IN **4}
        for meashure in MEASHURES.keys():
            res = round(value / MEASHURES.get(meashure), 2)
            if res < 1000:
                return f"{res} {meashure}"

    @staticmethod
    async def __file_reader(path_to_file: str, lines: bool = False) -> str:
        """Интерфейс для чтения файлов

        Args:
            path_to_file (str): путь к файлу

        Returns:
            str: содержимое файла
        """
        with open(f'{path_to_file}', 'r', encoding='utf-8') as file:
            if lines:
                return file.readlines()
            return file.read()

    @staticmethod
    async def __file_writer(path_to_file: str, content: str, lines: bool = False) -> None:
        """Интерфейс для записи файлов

        Args:
            path_to_file (str): путь к файлу
            content (str): данные для записи
        """
        with open(f'{path_to_file}', 'w', encoding='utf-8') as file:
            if lines:
                file.writelines(content)
            else:
                file.write(content)

    def __init__(self, user_object: DbUser, wg_user_model: WGUserModel) -> None:
        self.user_object = user_object
        self.wg_user_model = wg_user_model
        if len(self.user_object.user_name) > 14:
            self.user_object.user_name = self.user_object.user_name[:15]

    def __str__(self) -> str:
        send = self.__convert_from_bytes(self.wg_user_model.send)
        received = self.__convert_from_bytes(self.wg_user_model.received)
        keys_ru = ('Имя', 'Локальный адрес', 'Статус', 'Внешний адрес/порт', 'Появлялся', 'Трафик')
        values = (
            self.user_object.user_name, 
            str(self.user_object.ip), 
            'заблокирован' if self.user_object.
            is_baned else 'активен', 
            self.wg_user_model.endpoint, 
            self.__time_data_prepare(), 
            f"{send} загружено, {received} отправлено")
        result = '\n'.join(map(lambda x: f"<b>{x[0]}:</b> <code>{x[1]}</code>", zip(keys_ru, values)))
        return result