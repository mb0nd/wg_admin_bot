import os
from typing import Dict, Tuple
from aiogram.types import FSInputFile

async def genKeys (name :str) -> None:
    try:
        os.mkdir(f"/etc/wireguard/{name}")
    except FileExistsError:
        pass
    os.system (f"wg genkey | tee /etc/wireguard/{name}/{name}_privatekey | wg pubkey > /etc/wireguard/{name}/{name}_pubkey")

async def getEnv(name :str) -> Dict:
    env={}
    with open(f'/etc/wireguard/{name}/{name}_pubkey', 'r', encoding='utf-8') as file:
        env['publickey'] = file.read().strip()
    with open(f'/etc/wireguard/{name}/{name}_privatekey', 'r', encoding='utf-8') as file:
        env['privatekey'] = file.read().strip()
    with open('/etc/wireguard/publickey', 'r', encoding='utf-8') as file:
        env['serverPublickey'] = file.read().strip()
    with open('last_ip', 'r', encoding='utf-8') as file:
        ip = file.read().strip().split('.')
    ip[-1] = str(int(ip[-1])+1)
    env['current_ip'] = '.'.join(ip)
    env['hostname'] = os.uname().nodename
    return env
    
async def setNewPeer(publickey :str, current_ip :str) -> None:
    with open('/etc/wireguard/wg0.conf', 'a', encoding='utf-8') as file:
        file.write(f"\n[Peer]\nPublicKey = {publickey}\nAllowedIPs = {current_ip}/32")
    os.system ( f"wg set wg0 peer {publickey} allowed-ips {current_ip}/32")

async def generatePeerConfig(name: str,data: dict, port: str) -> None:
    with open(f'/etc/wireguard/{name}/{name}.conf', 'w', encoding='utf-8') as file:
        file.write(
            f"[Interface]\nPrivateKey = {data['privatekey']}\nAddress = {data['current_ip']}/32\n"
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {data['serverPublickey']}\n"
            f"Endpoint = {data['hostname']}:{port}\n"
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        )

async def writeLastIp(ip :str) -> None:
    with open('last_ip', 'w', encoding='utf-8') as file:
        file.write(ip)

async def addUser(name :str, port: str) -> Tuple:
    await genKeys(name)
    data = await getEnv(name)
    await setNewPeer(data['publickey'], data['current_ip'])
    await generatePeerConfig(name, data, port)
    await writeLastIp(data['current_ip'])
    config = FSInputFile(f'/etc/wireguard/{name}/{name}.conf', filename=f'{name}.conf')
    return (data['publickey'], data['current_ip'], config)

async def blocked_user(key: str) -> None:
    os.system(f'wg set wg0 peer {key} remove')
    with open('/etc/wireguard/wg0.conf', 'r', encoding='utf-8') as f:
        input_text = f.read()
    output_text = input_text.replace(key, f"%BANNED%{key}")
    with open('/etc/wireguard/wg0.conf', 'w', encoding='utf-8') as f:
        f.write(output_text)

async def unblocked_user(key: str, ip: str) -> None:
    os.system(f'wg set wg0 peer {key} allowed-ips {ip}/32')
    with open('/etc/wireguard/wg0.conf', 'r', encoding='utf-8') as f:
        input_text = f.read()
    output_text = input_text.replace(f"%BANNED%{key}", key)
    with open('/etc/wireguard/wg0.conf', 'w', encoding='utf-8') as f:
        f.write(output_text)