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
        ip = file.read()
    env['current_ip']=ip[:-1]+str(int(ip[-1])+1)
    env['listen_port'] = os.getenv('LISTEN_PORT')
    env['hostname'] = os.uname().nodename
    return env
    
async def setNewPeer(publickey :str, current_ip :str) -> None:
    with open('/etc/wireguard/wg0.conf', 'a', encoding='utf-8') as file:
        file.write(f"\n[Peer]\nPublicKey = {publickey}\nAllowedIPs = {current_ip}/32")
    os.system ( f"wg set wg0 peer {publickey} allowed-ips {current_ip}/32")

async def generatePeerConfig(name :str,data :dict) -> None:
    with open(f'/etc/wireguard/{name}/{name}.conf', 'w', encoding='utf-8') as file:
        file.write(
            f"[Interface]\nPrivateKey = {data['privatekey']}\nAddress = {data['current_ip']}/32\n"
            f"DNS = 8.8.8.8\n[Peer]\nPublicKey = {data['serverPublickey']}\n"
            f"Endpoint = {data['hostname']}:{data['listen_port']}\n"
            "AllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 20"
        )

async def writeLastIp(ip :str) -> None:
    with open('last_ip', 'w', encoding='utf-8') as file:
        file.write(ip)

async def addUser(name :str) -> Tuple:
    await genKeys(name)
    data = await getEnv(name)
    await setNewPeer(data['publickey'], data['current_ip'])
    await generatePeerConfig(name, data)
    await writeLastIp(data['current_ip'])
    config = FSInputFile(f'/etc/wireguard/{name}/{name}.conf', filename=f'{name}.conf')
    return (data['publickey'], data['current_ip'], config)