import os

import keyring

PORT = "1080"

def get_proxys(file_path: str = None) -> list[str]:
    path = file_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")
    with open(path, "r") as f:
        ips = f.read().split(",")

    username = keyring.get_password("nordvpn1", "username")
    password = keyring.get_password("nordvpn1", "password")

    return [f"socks5h://{username}:{password}@{ip}:{PORT}" for ip in ips]

