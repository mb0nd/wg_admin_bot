from aiogram.types import FSInputFile
from env_reader import env
import os

class WgUser:
    @staticmethod
    def file_reader(path_to_file: str):
        with open(f'{path_to_file}', 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def file_writer(path_to_file: str, content: str):
        with open(f'{path_to_file}', 'w', encoding='utf-8') as file:
            file.write(content)

    path_to_wg = env.path_to_wg
    hostname = os.uname().nodename
    serverPublickey = file_reader(f'{path_to_wg}publickey')

    def __init__(self, name: str) -> None:
        self.path_to_user = WgUser.path_to_wg + name
        if not os.path.exists(self.path_to_user):
            os.mkdir(f"{self.path_to_user}")
        os.system (f"wg genkey | tee {self.path_to_user}/{name}_privatekey | wg pubkey > {self.path_to_user}/{name}_pubkey")
        self.name = name
        self.publickey = WgUser.file_reader(f"{self.path_to_user}/{name}_pubkey").strip()
        self.privatekey = WgUser.file_reader(f"{self.path_to_user}/{name}_privatekey").strip()
        ip = WgUser.file_reader("last_ip").strip().split('.')
        ip[-1] = str(int(ip[-1])+1)
        self.current_ip = '.'.join(ip)

    async def set_new_peer(self):
        with open(f'{WgUser.path_to_wg}wg0.conf', 'a', encoding='utf-8') as file:
            file.write(f"\n[Peer]\nPublicKey = {self.publickey}\nAllowedIPs = {self.current_ip}/32")
        os.system ( f"wg set wg0 peer {self.publickey} allowed-ips {self.current_ip}/32")

    async def generate_peer_config(self):
        content = f"[Interface]\nPrivateKey = {self.privatekey}\nAddress = {self.current_ip}/32\n"\
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {self.serverPublickey}\n"\
            f"Endpoint = {self.hostname}:{env.listen_port}\n"\
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        WgUser.file_writer(f'{self.path_to_user}/{self.name}.conf', content)

    async def add_user(self):
        await self.set_new_peer()
        await self.generate_peer_config()
        await WgUser.file_writer('last_ip', self.current_ip)
        config = await FSInputFile(f'{self.path_to_user}/{self.name}.conf', filename=f'{self.name}.conf')
        return (self.publickey, self.current_ip, config)

""" def blocked_user(self, status: bool):
        input_text = WgUser.file_reader(f"{WgUser.path_to_wg}wg0.conf")
        if status:
            os.system(f'wg set wg0 peer {self.publickey} remove')
            output_text = input_text.replace(self.publickey, f"%BANNED%{self.publickey}")
        else:
            os.system(f'wg set wg0 peer {self.publickey} allowed-ips {self.current_ip}/32')
            output_text = input_text.replace(f"%BANNED%{self.publickey}", self.publickey)
        WgUser.file_writer(f"{WgUser.path_to_wg}wg0.conf", output_text)"""




a = WgUser('ivan')
print(a.hostname)
print(a.name)
print(a.path_to_user)
print(a.path_to_wg)
print(a.publickey)
print(a.privatekey)
print(a.current_ip)

