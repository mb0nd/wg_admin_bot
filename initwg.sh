#!/usr/bin/env bash

if [ ! -f /etc/wireguard/wg0.conf ]; then
    wg genkey | tee /etc/wireguard/privatekey | wg pubkey | tee /etc/wireguard/publickey
    chmod 600 /etc/wireguard/privatekey
    echo -e "[Interface]\nPrivateKey = $(cat /etc/wireguard/privatekey)\nAddress = 10.0.0.1/24\nListenPort = 51830\nPostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE\nPostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE" > /etc/wireguard/wg0.conf
fi
wg-quick up wg0
python3 bot/__main__.py