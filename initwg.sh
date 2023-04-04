#!/usr/bin/env bash

if [ ! -f "$PATH_TO_WG"wg0.conf ]; then
    wg genkey | tee "$PATH_TO_WG"privatekey | wg pubkey | tee "$PATH_TO_WG"publickey
    chmod 600 "$PATH_TO_WG"privatekey
    echo -e "[Interface]\nPrivateKey = $(cat "$PATH_TO_WG"privatekey)\nAddress = 10.0.0.1/24\nListenPort = "$LISTEN_PORT"\nPostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o `ip route | awk '/default/ {print $5; exit}'` -j MASQUERADE\nPostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o `ip route | awk '/default/ {print $5; exit}'` -j MASQUERADE" > "$PATH_TO_WG"wg0.conf
    chmod 600 "$PATH_TO_WG"wg0.conf
fi
wg-quick up wg0
python3 bot/__main__.py