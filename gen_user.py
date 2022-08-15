import os
import subprocess
from typing import Dict, List, Tuple
from aiogram.types import FSInputFile
from typing import Union
from db.models import User

async def genKeys (name :str, path_to_wg: str) -> None:
    try:
        os.mkdir(f"{path_to_wg}{name}")
    except FileExistsError:
        pass
    os.system (f"wg genkey | tee {path_to_wg}{name}/{name}_privatekey | wg pubkey > {path_to_wg}{name}/{name}_pubkey")

async def getEnv(name :str, path_to_wg: str) -> Dict:
    env={}
    with open(f'{path_to_wg}{name}/{name}_pubkey', 'r', encoding='utf-8') as file:
        env['publickey'] = file.read().strip()
    with open(f'{path_to_wg}{name}/{name}_privatekey', 'r', encoding='utf-8') as file:
        env['privatekey'] = file.read().strip()
    with open(f'{path_to_wg}publickey', 'r', encoding='utf-8') as file:
        env['serverPublickey'] = file.read().strip()
    with open('last_ip', 'r', encoding='utf-8') as file:
        ip = file.read().strip().split('.')
    ip[-1] = str(int(ip[-1])+1)
    env['current_ip'] = '.'.join(ip)
    env['hostname'] = os.uname().nodename
    return env
    
async def setNewPeer(publickey :str, current_ip :str, path_to_wg: str) -> None:
    with open(f'{path_to_wg}wg0.conf', 'a', encoding='utf-8') as file:
        file.write(f"\n[Peer]\nPublicKey = {publickey}\nAllowedIPs = {current_ip}/32")
    os.system ( f"wg set wg0 peer {publickey} allowed-ips {current_ip}/32")

async def generatePeerConfig(name: str,data: dict, port: str, path_to_wg: str) -> None:
    with open(f'{path_to_wg}{name}/{name}.conf', 'w', encoding='utf-8') as file:
        file.write(
            f"[Interface]\nPrivateKey = {data['privatekey']}\nAddress = {data['current_ip']}/32\n"
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {data['serverPublickey']}\n"
            f"Endpoint = {data['hostname']}:{port}\n"
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        )

async def writeLastIp(ip :str) -> None:
    with open('last_ip', 'w', encoding='utf-8') as file:
        file.write(ip)

async def addUser(name :str, port: str, path_to_wg: str) -> Tuple:
    await genKeys(name, path_to_wg)
    data = await getEnv(name, path_to_wg)
    await setNewPeer(data['publickey'], data['current_ip'], path_to_wg)
    await generatePeerConfig(name, data, port, path_to_wg)
    await writeLastIp(data['current_ip'])
    config = FSInputFile(f'{path_to_wg}{name}/{name}.conf', filename=f'{name}.conf')
    return (data['publickey'], data['current_ip'], config)

async def blocked_user(key: str, path_to_wg: str) -> None:
    os.system(f'wg set wg0 peer {key} remove')
    with open(f'{path_to_wg}wg0.conf', 'r', encoding='utf-8') as f:
        input_text = f.read()
    output_text = input_text.replace(key, f"%BANNED%{key}")
    with open(f'{path_to_wg}wg0.conf', 'w', encoding='utf-8') as f:
        f.write(output_text)

async def unblocked_user(key: str, ip: str, path_to_wg: str) -> None:
    os.system(f'wg set wg0 peer {key} allowed-ips {ip}/32')
    with open(f'{path_to_wg}wg0.conf', 'r', encoding='utf-8') as f:
        input_text = f.read()
    output_text = input_text.replace(f"%BANNED%{key}", key)
    with open(f'{path_to_wg}wg0.conf', 'w', encoding='utf-8') as f:
        f.write(output_text)

async def remove_user(user: User, path_to_wg: str):
    os.system(f'wg set wg0 peer {user.pub_key} remove')
    with open(f'{path_to_wg}wg0.conf', 'r', encoding='utf-8') as f:
        input_text = f.readlines()
    for i in range(len(input_text)):
        if user.pub_key in input_text[i]:
            for _ in range(3):
                input_text.pop(i-1)
            break
    with open(f'{path_to_wg}wg0.conf', 'w', encoding='utf-8') as f:
        f.writelines(input_text)
    os.system(f'rm -rf {path_to_wg}{user.user_name}')

async def check_statistics() -> List[Dict]:
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

async def data_preparation(data_db: Union[list, User]) -> str:
    data_cmd = await check_statistics()
    res=''
    for peer in data_cmd:
        for user in data_db:
            if peer['peer'] == user.pub_key:
                if peer.get('endpoint'):
                    res += f"<b>Имя:</b> <code>{user.user_name}</code>\n<b>Локальный адрес:</b> <code>{user.ip}</code>\n<b>Активен:</b> <code>{'нет' if user.is_baned else 'да'}</code>\n<b>Внешний адрес/порт</b>: <code>{peer['endpoint']}</code>\n<b>Появлялся:</b> <code>{peer['latest handshake']}</code>\n<b>Трафик:</b> <code>{peer['transfer']}</code>\n{'_'*50}\n"
                else:
                    res += f"<b>Имя:</b> <code>{user.user_name}</code>\n<b>Локальный адрес:</b> <code>{user.ip}</code>\n<b>Активен:</b> <code>{'нет' if user.is_baned else 'да'}</code>\n{'_'*50}\n"
                break
    if not res:
        return 'Нет такого пользователя в wireguard'
    return res