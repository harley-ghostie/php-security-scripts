# PHP Security PoCs
![Status](https://img.shields.io/badge/STATUS-EM%20DESENVOLVIMENTO-brightgreen?style=for-the-badge)
> [!NOTE]
> Projeto em desenvolvimento.
>
> Este repositório reúne scripts de apoio para validação técnica e triagem de segurança. Os scripts podem passar por ajustes, refatoração e melhorias de precisão conforme novos cenários forem testados.

Repositório com scripts para reconhecimento, triagem e validação controlada de vulnerabilidades em aplicações PHP.

Os scripts foram separados por nível de profundidade, começando por reconhecimento básico até validações mais avançadas de cadeia de exploração.

---

## Visão geral dos scripts

| Script | Objetivo | Quando usar |
|---|---|---|
| `php_recon_scanner.py` | Reconhecimento inicial de exposição PHP | Usar no começo da análise para mapear arquivos sensíveis, headers, backups, erros e possíveis sinais de LFI/RFI. |
| `php_scanner_LFI.py` | Validação básica de LFI, deserialização e `phpinfo()` | Usar após o reconhecimento, quando houver suspeita de parâmetros vulneráveis ou páginas de debug expostas. |
| `php_vuln_triage.py` | Validação de cadeia com `phpinfo()`, upload e possível LFI | Usar quando já existe indício de `phpinfo()` exposto e algum endpoint de upload conhecido. |
| `php_poc_lfi_rce.py` | PoC avançada de cadeia LFI para possível RCE | Usar somente em ambiente autorizado, controlado ou laboratório, quando for necessário demonstrar impacto técnico mais alto. |

---

# Fluxo recomendado de uso

A ordem mais lógica para utilização dos scripts é:

```text
1. php_recon_scanner.py
   ↓
2. php_scanner_LFI.py
   ↓
3. php_vuln_triage.py
   ↓
4. php_poc_lfi_rce.py
```

## Explicação rápida do fluxo

Primeiro, use o `php_recon_scanner.py` para identificar possíveis exposições e pontos de interesse. Depois, use o `php_scanner_LFI.py` para validar indícios básicos de vulnerabilidade. Caso existam sinais de `phpinfo()` exposto, upload acessível e possível LFI, avance para o `php_vuln_triage.py`. O `php_poc_lfi_rce.py` deve ser usado apenas em cenários controlados, pois possui funcionalidades com potencial de impacto maior.

---

# Scripts

## php_recon_scanner.py

### Descrição

O `php_recon_scanner.py` é um scanner de reconhecimento para aplicações PHP. Ele realiza uma análise inicial em busca de exposições comuns, arquivos sensíveis, páginas de debug, arquivos de backup, mensagens de erro e possíveis indícios de LFI/RFI.

### O que o script faz

- Verifica headers HTTP em busca de indícios de PHP;
- Procura arquivos e paths sensíveis;
- Testa páginas como `phpinfo.php`, `info.php` e `test.php`;
- Verifica exposição de `.env`, `.git/config`, `config.php`, `wp-config.php` e arquivos similares;
- Testa existência de arquivos de backup e dumps;
- Busca mensagens de erro PHP;
- Testa payloads básicos de LFI/RFI no parâmetro `file`;
- Verifica diretórios comuns como `admin/`, `uploads/`, `backup/`, `logs/` e `phpmyadmin/`.

### Cenário de uso

Use este script no início da análise, quando ainda não há uma vulnerabilidade confirmada. Ele serve para mapear rapidamente a superfície da aplicação PHP e indicar quais pontos merecem validação manual ou testes mais específicos.

### Como usar

```bash
python3 php_recon_scanner.py --url https://exemplo.com/
```

### Quando usar cada formato

Use https://exemplo.com/ quando a aplicação PHP estiver na raiz do domínio. 
Use `https://exemplo.com/app/`  quando a aplicação estiver dentro de um diretório específico.

```bash
python3 php_recon_scanner.py --url https://exemplo.com/
```

Observação

Não coloque uma página específica como `phpinfo.php` ou `index.php` nesse script. Ele precisa de uma base para testar vários caminhos, como:
```bash
phpinfo.php
.env
.git/config
config.php
wp-config.php
backup.zip
admin/
uploads/
```
---

## php_scanner_LFI.py

### Descrição

O `php_scanner_LFI.py` realiza testes básicos para identificar possíveis vulnerabilidades comuns em aplicações PHP, com foco em LFI, deserialização insegura e exposição de páginas `phpinfo()`.

### O que o script faz

- Testa parâmetros comuns como `page`, `file`, `inc`, `include` e `template`;
- Envia payloads básicos para identificar possível Local File Inclusion;
- Testa payload simples de deserialização PHP;
- Procura páginas de debug como `phpinfo.php`, `info.php` e `test.php`;
- Exibe no terminal os achados identificados.

### Cenário de uso

Use este script após a etapa de reconhecimento, principalmente quando houver suspeita de parâmetros vulneráveis ou páginas de debug expostas. Ele funciona como uma triagem técnica para confirmar indícios antes de uma validação mais profunda.

### Como usar

Antes de executar, ajuste a variável `TARGET` no início do script:

```python
TARGET = "https://exemplo.com/index.php"
```
```python
TARGET = "https://exemplo.com/app/page.php"
```
### Cenário ideal
Use uma rota ou endpoint da aplicação que aceite parâmetros via GET.

Esse script testa parâmetros como:
```bash
?page=
?file=
?inc=
?include=
?template=
```
Então o melhor alvo é uma rota onde faria sentido existir carregamento dinâmico de páginas, templates ou arquivos.

Exemplo do teste gerado:
```bash
https://exemplo.com/index.php?file=../../../../etc/passwd
```
### Execução:

```bash
python3 php_scanner_LFI.py
```

---

## php_vuln_triage.py

### Descrição

O `php_vuln_triage.py` é uma PoC para validação de uma possível cadeia envolvendo exposição de `phpinfo()`, upload de arquivo e inclusão local de arquivo.

O script tenta identificar o caminho temporário do PHP, enviar um arquivo disfarçado como imagem e acionar esse arquivo por meio de um possível parâmetro vulnerável.

### O que o script faz

- Acessa uma página `phpinfo.php`;
- Tenta identificar o caminho temporário utilizado pelo PHP;
- Envia um arquivo de teste disfarçado como imagem GIF;
- Tenta acionar o arquivo enviado por meio de possível LFI;
- Exibe no terminal o resultado da tentativa.

### Cenário de uso

Use este script quando já existir uma suspeita mais concreta de cadeia explorável, especialmente quando houver:

- página `phpinfo()` exposta;
- endpoint de upload conhecido;
- suspeita de LFI;
- necessidade de validar se as falhas podem ser combinadas.

### Compatibilidade com sistemas servidores

Este script não é exclusivo para Windows. Na versão atual, ele está mais compatível com servidores Linux/Unix, pois procura caminhos temporários no formato `/tmp`.

Em servidores Windows, o script pode precisar de ajuste nos padrões de busca do diretório temporário, pois os caminhos costumam seguir formatos como:

```text
C:\Windows\Temp
C:\xampp\tmp
C:\wamp64\tmp
```

Resumo prático:

| Sistema | Compatibilidade |
|---|---|
| Linux/Unix | Maior compatibilidade no formato atual |
| Windows | Pode exigir ajuste nos caminhos e regex |
| XAMPP/WAMP | Pode exigir ajuste no caminho temporário e endpoint de upload |

### Como usar

Antes de executar, ajuste as variáveis no início do script:

```python
BASE = "https://exemplo.com/phpinfo.php"
BASE = "https://exemplo.com/app/phpinfo.php"
UPLOAD_FORM = "http://www.site.com.br/app/upload.php"
```

### Path ideal para `UPLOAD_FORM`

O `UPLOAD_FORM` deve apontar diretamente para o endpoint responsável pelo upload de arquivos.

Exemplos:
```python
UPLOAD_FORM = "https://exemplo.com/upload.php"
UPLOAD_FORM = "https://exemplo.com/app/upload.php"
```

### Execução:

```bash
python3 php_vuln_triage.py
```

---

## php_poc_lfi_rce.py

### Descrição

O `php_poc_lfi_rce.py` é uma PoC avançada para validação de uma cadeia de exploração em aplicações PHP. Ele tenta combinar exposição de `phpinfo()`, upload inseguro, LFI e possível execução de comandos.

Este script deve ser tratado como uma validação de alto impacto.

### O que o script faz

- Acessa uma página `phpinfo.php`;
- Tenta identificar o diretório temporário de upload do PHP;
- Testa múltiplos endpoints comuns de upload;
- Testa diferentes nomes de campos de upload;
- Envia arquivo de teste disfarçado como imagem;
- Tenta acionar o arquivo por meio de parâmetros comuns de LFI;
- Possui funções adicionais relacionadas a pós-exploração.

### Cenário de uso

Use este script somente em ambiente autorizado, laboratório, CTF ou teste formal de segurança com escopo explícito.

Ele é indicado quando já existe uma hipótese técnica forte de que a aplicação pode permitir uma cadeia de exploração mais severa, como LFI levando a execução de comandos.

Use esse script quando você quer validar uma cadeia mais avançada e já existe suspeita de:

```python
phpinfo() exposto
upload acessível
possível LFI
possível execução de comando
```


Não é recomendado usar este script como primeira etapa de análise.

### Compatibilidade com sistemas servidores

O script foi escrito com foco maior em ambientes Linux/Unix, principalmente por utilizar caminhos e comandos comuns desse tipo de sistema.

Algumas partes podem não funcionar corretamente em servidores Windows sem adaptação, especialmente funções relacionadas a comandos do sistema, caminhos de arquivos e shell reverso.

Resumo prático:

| Sistema | Compatibilidade |
|---|---|
| Linux/Unix | Compatibilidade maior |
| Windows | Requer adaptação de caminhos e comandos |
| Servidores Apache/Nginx com PHP-FPM | Pode ser aplicável, dependendo da configuração |
| XAMPP/WAMP | Pode exigir ajustes nos diretórios e endpoints |

### Como usar

Antes de executar, ajuste as variáveis no início do script:

```python
BASE = "http://www.site.com.br/app/"
ATTACKER_IP = "SEU_IP_AUTORIZADO"
ATTACKER_PORT = 4444
```

### Path ideal

Use a URL base do diretório onde estão os recursos da aplicação PHP, com barra no final.
Exemplos:
```python
BASE = "https://exemplo.com/"
BASE = "https://exemplo.com/app/"
```

### Por que precisa ser a base?

Porque o script monta automaticamente caminhos como:
```python
PHPINFO_URL = urljoin(BASE, "phpinfo.php")
```

E também testa endpoints como:
```python
upload.php
enviar.php
submit.php
upload_image.php
```

### 

Depois execute:

```bash
python3 php_poc_lfi_rce.py
```

---

# Requisitos

Os scripts requerem Python 3.

Instale a dependência principal:

```bash
pip install requests
```

---

# Observações importantes

Os scripts possuem finalidades diferentes e não devem ser executados todos de forma automática sem análise prévia.

O `php_recon_scanner.py` e o `php_scanner_LFI.py` são mais indicados para triagem e reconhecimento. Já o `php_vuln_triage.py` e o `php_poc_lfi_rce.py` devem ser usados com mais cautela, pois tentam validar cadeias de exploração com impacto potencial maior.

Os resultados devem sempre ser revisados manualmente. Respostas customizadas, WAF, páginas de erro, redirecionamentos, autenticação, diferenças entre Linux e Windows e configurações específicas do servidor podem gerar falsos positivos ou falsos negativos.

---

# Recomendações de mitigação

Para reduzir os riscos validados por estes scripts, recomenda-se remover páginas `phpinfo()` de ambientes produtivos, restringir endpoints administrativos, validar corretamente arquivos enviados por upload, bloquear extensões executáveis, armazenar uploads fora do webroot, desabilitar execução de scripts em diretórios de upload, corrigir pontos de LFI e revisar o uso de deserialização em PHP.

Também é recomendado revisar permissões de arquivos, configurações do servidor web, exposição de arquivos sensíveis, diretórios públicos, backups acessíveis e logs de acesso para identificar possíveis tentativas de exploração.

---

# Observação de segurança

Estes scripts devem ser utilizados apenas em ambientes autorizados.

Alguns testes podem acessar arquivos sensíveis, validar execução de código ou demonstrar cadeias de exploração com impacto real. Portanto, o uso deve estar alinhado ao escopo formal do teste e às regras de engajamento acordadas.

Antes de qualquer execução em ambiente produtivo, revise o código, entenda o impacto de cada função e remova qualquer ação que não seja necessária para a validação acordada.

---

# Aviso legal

O uso destes scripts contra sistemas sem autorização é proibido.

A finalidade deste repositório é exclusivamente apoiar atividades legítimas de segurança, como pentest autorizado, validação de vulnerabilidades, laboratório, estudo técnico e demonstração controlada de risco.
