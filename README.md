# PHP Exploitation PoCs

Repositório com scripts de apoio para validação controlada de vulnerabilidades comuns em aplicações PHP.

Os scripts têm como objetivo auxiliar atividades autorizadas de segurança ofensiva, pentest, análise técnica e demonstração de risco em ambientes controlados.

## Visão geral

Este repositório contém três scripts com níveis diferentes de profundidade:

| Script | Finalidade | Nível |
|---|---|---|
| `exploit_php.py` | Triagem inicial de falhas comuns em PHP | Básico |
| `exploit_php2.py` | Validação de cadeia envolvendo `phpinfo()`, upload e LFI | Intermediário |
| `exploit_php3.py` | PoC avançada com tentativa de exploração encadeada e pós-exploração | Avançado |

## Resumo dos scripts

### `exploit_php.py`

O `exploit_php.py` realiza uma validação inicial de vulnerabilidades comuns em aplicações PHP. Ele testa indícios de Local File Inclusion (LFI), deserialização insegura e exposição de páginas de debug com `phpinfo()`.

Esse script é indicado para triagem inicial, quando o objetivo é verificar rapidamente se existem sinais básicos de falhas PHP no ambiente analisado.

### `exploit_php2.py`

O `exploit_php2.py` valida uma cadeia específica envolvendo exposição de `phpinfo()`, upload de arquivo e possível inclusão local de arquivo (LFI).

Esse script é indicado quando já existe suspeita de `phpinfo()` exposto e algum endpoint de upload conhecido. Ele ajuda a verificar se essas condições podem ser combinadas para uma exploração mais relevante.

### `exploit_php3.py`

O `exploit_php3.py` automatiza uma cadeia mais avançada de exploração. Ele tenta identificar o diretório temporário do PHP, testar endpoints e campos de upload, validar LFI e executar funções adicionais relacionadas à pós-exploração.

Esse script deve ser usado somente em laboratório, CTF ou pentest formal com escopo explícito, pois contém funcionalidades com potencial de alto impacto.

---

# Scripts

## exploit_php.py

### Descrição

O `exploit_php.py` é um script de triagem inicial para identificar possíveis vulnerabilidades comuns em aplicações PHP.

Ele realiza testes básicos para verificar indícios de:

- Local File Inclusion (LFI);
- deserialização insegura em PHP;
- exposição de páginas de debug com `phpinfo()`.

### O que o script faz

- Testa parâmetros comuns em busca de possível LFI;
- Envia payloads básicos para verificar indícios de deserialização insegura;
- Procura páginas comuns como `phpinfo.php`, `info.php` e `test.php`;
- Exibe no terminal os resultados encontrados.

### Cenário de uso

Este script é indicado para uma primeira análise técnica, quando ainda não há confirmação da vulnerabilidade e o objetivo é apenas identificar sinais iniciais de exposição ou comportamento inseguro.

Ele deve ser usado como etapa de reconhecimento e validação preliminar, não como prova definitiva de exploração.

---

## exploit_php2.py

### Descrição

O `exploit_php2.py` é uma Prova de Conceito para validação de uma possível cadeia de exploração envolvendo exposição de `phpinfo()`, upload de arquivo e inclusão local de arquivo.

O script tenta identificar o caminho temporário utilizado pelo PHP, enviar um arquivo disfarçado como imagem e acionar esse arquivo por meio de um possível parâmetro vulnerável.

### O que o script faz

- Acessa uma página `phpinfo.php` exposta;
- Tenta identificar o caminho temporário de upload do PHP;
- Realiza upload de um arquivo de teste disfarçado como imagem;
- Tenta acionar o arquivo enviado por meio de LFI;
- Exibe o resultado da tentativa no terminal.

### Cenário de uso

Este script é indicado quando já existe suspeita ou confirmação de que a aplicação possui:

- página `phpinfo()` exposta;
- funcionalidade de upload acessível;
- possível parâmetro vulnerável a LFI.

Ele deve ser usado para validar se essas condições podem ser combinadas em uma cadeia real de exploração.

---

## exploit_php3.py

### Descrição

O `exploit_php3.py` é uma PoC avançada para validação de cadeia ofensiva em aplicações PHP.

Ele tenta automatizar múltiplas etapas, incluindo identificação do diretório temporário do PHP, fuzzing de endpoints de upload, teste de campos de upload, tentativa de LFI e validações adicionais de pós-exploração.

### O que o script faz

- Acessa uma página `phpinfo.php`;
- Tenta identificar o diretório temporário de upload;
- Testa múltiplos endpoints comuns de upload;
- Testa diferentes nomes de campos de upload;
- Envia arquivo de teste disfarçado como imagem;
- Tenta acionar o arquivo por meio de parâmetros comuns de LFI;
- Possui funções adicionais relacionadas à pós-exploração.

### Cenário de uso

Este script deve ser utilizado somente em ambientes controlados, laboratórios, CTFs ou testes formais com autorização explícita.

Por conter funcionalidades com potencial de alto impacto, ele não é recomendado para triagem simples nem para execução direta em ambientes produtivos sem validação prévia do escopo e dos riscos.

Antes de usar em um teste real, recomenda-se revisar o código e desabilitar qualquer função que não seja necessária para a comprovação técnica acordada.

---

# Requisitos

Os scripts requerem Python 3.

Dependência principal:

```bash
pip install requests
```

---

# Como usar

Antes de executar qualquer script, ajuste as variáveis de alvo no início do arquivo correspondente.

Exemplo:

```python
TARGET = "http://www.site.com.br/math/avaliacao"
```

ou:

```python
BASE = "http://www.site.com.br/math/avaliacao/"
```

Depois, execute o script desejado:

```bash
python3 exploit_php.py
```

```bash
python3 exploit_php2.py
```

```bash
python3 exploit_php3.py
```

---

# Estrutura sugerida

```text
php-exploitation-pocs/
├── exploit_php.py
├── exploit_php2.py
├── exploit_php3.py
└── README.md
```

---

# Recomendações de mitigação

Para reduzir o risco das falhas validadas por estes scripts, recomenda-se remover páginas `phpinfo()` de ambientes produtivos, restringir endpoints administrativos, validar corretamente arquivos enviados por upload, bloquear extensões executáveis, armazenar uploads fora do webroot, desabilitar execução de scripts em diretórios de upload, corrigir pontos de LFI e revisar o uso de deserialização em PHP.

Também é recomendado revisar permissões de arquivos, segredos expostos, configurações do servidor web e logs de acesso para identificar possíveis tentativas de exploração.

---

# Observação de segurança

Estes scripts devem ser utilizados apenas em ambientes autorizados.

Alguns testes podem acessar arquivos sensíveis, validar execução de código ou demonstrar cadeias de exploração com impacto real. Portanto, o uso deve estar alinhado ao escopo formal do teste e às regras de engajamento acordadas.

Os resultados devem ser analisados manualmente antes de qualquer conclusão, pois respostas customizadas, WAF, páginas de erro e diferenças de configuração podem gerar falsos positivos ou falsos negativos.

---

# Aviso legal

O uso destes scripts contra sistemas sem autorização é proibido.

A finalidade deste repositório é exclusivamente apoiar atividades legítimas de segurança, como pentest autorizado, validação de vulnerabilidades, laboratório, estudo técnico e demonstração controlada de risco.
