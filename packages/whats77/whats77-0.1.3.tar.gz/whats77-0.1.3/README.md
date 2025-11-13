# Whats77

**Versão:** 1.0.0
**Compatibilidade:** Retrocompatível com versões 0.1.x
**Backend:** Whats77 Manager (FastAPI + Redis + Z-API)

---

## 📘 Visão Geral

O **Whats77** é um *facilitador* para o envio de mensagens via WhatsApp através da **Z-API**, agora totalmente integrado ao **Whats77 Manager** — um orquestrador que cuida de cadência, idempotência, retentativas automáticas e segurança via API Key.

Com esta nova integração, suas automações **não precisam mais chamar a Z-API diretamente**.
Basta chamar os mesmos métodos (`send_text`, `send_image`, `send_audio`, `send_document`) e o Manager fará todo o controle de fila e envio.

---

## 🧱 Arquitetura do Manager

```
whats77_manager/
├── apps/
│   ├── manager_api.py     # FastAPI: /enqueue, /status, /health
│   ├── worker.py          # Worker: consome fila e dispara via Z-API
│   ├── rate_limiter.py    # Controle de cadência (Redis)
│   ├── scheduler.py       # Retentativas e backoff exponencial
│   ├── storage.py         # Idempotência e DLQ
│   ├── models.py          # Schemas (MessageJob, SendResult)
│   └── zapi_client/
│       ├── whats77.py     # Cliente HTTP direto na Z-API
│       └── senders.py     # Multi-instâncias Z-API
└── .env
```

O **Manager** atua como intermediário:

* ✅ Controla limites e cadência
* ✅ Evita envios duplicados (idempotência)
* ✅ Distribui mensagens entre múltiplas instâncias Z-API
* ✅ Tenta novamente em caso de falha temporária
* 🔒 Requer **API Key** (`X-API-Key`) para autenticação

---

## ⚙️ Configuração

### Arquivo `.env`

Crie um arquivo `.env` na raiz do seu projeto:

```env
MANAGER_URL=http://localhost:8000
MANAGER_API_KEY=meu_token_super_seguro
SENDER_ID=0
```

> 🔁 Compatibilidade:
> Se as variáveis acima não existirem, o código tenta usar:
> `INSTANCE_ID`, `TOKEN`, `SECURITY_TOKEN` (modo legado).

---

### Configuração Manual

```python
from whats77 import Whats77

# Inicialização manual (sem .env)
whatsapp = Whats77(
    manager_url="http://localhost:8000",
    manager_api_key="meu_token_super_seguro",
    sender_id="0"
)
```

---

## 🚀 Uso Rápido

### Inicializar

```python
from whats77 import Whats77
whatsapp = Whats77()  # carrega credenciais do .env
```

---

### Enviar Texto

```python
whatsapp.send_text(
    phone_number="+5511999999999",
    message="Olá! Esta mensagem foi enviada pelo Whats77 Manager."
)
```

---

### Enviar Imagem

Aceita **URL**, **data URI** ou **caminho local** (automaticamente convertido para base64):

```python
whatsapp.send_image(
    phone_number="+5511999999999",
    image_path_or_url="/tmp/imagem.jpg",
    caption="Segue imagem de teste"
)
```

> ⚙️ Parâmetros:
>
> * `view_once` (opcional, compatível; ignorado pelo Manager)
> * `is_base64` (opcional; mantido por compatibilidade)

---

### Enviar Documento

Também aceita caminho local ou data URI:

```python
whatsapp.send_document(
    phone_number="+5511999999999",
    file_path="/tmp/relatorio.pdf",
    document_type="pdf",
    caption="Segue o relatório."
)
```

---

### Enviar Áudio

```python
# converter áudio em base64
base64_audio = Whats77.parse_to_base64("/tmp/audio.mp3")

whatsapp.send_audio(
    phone_number="+5511999999999",
    base64_audio=base64_audio
)
```

---

## 🔢 Normalização de Números

```python
from whats77 import Whats77

n = Whats77.normalize_phone_number("11999999999")
print(n)  # 5511999999999

print(Whats77.is_valid_whatsapp_number("5511999999999"))
# True
```

---

## 🔐 Autenticação

Todas as requisições enviadas ao Manager contêm:

```
X-API-Key: <sua_chave>
Content-Type: application/json
```

Se a chave for inválida ou ausente:

```json
{"detail": "Invalid or missing API key"}
```

---

## 🧩 Compatibilidade com o Código Antigo

| Função antiga                                             | Mantida?                                 | Observações                           |
| --------------------------------------------------------- | ---------------------------------------- | ------------------------------------- |
| `send_text()`                                             | ✅                                        | Idêntica                              |
| `send_image()`                                            | ✅                                        | Aceita caminho local / URL / data URI |
| `send_audio()`                                            | ✅                                        | Idêntica                              |
| `send_document()`                                         | ✅                                        | Aceita caminho local / data URI       |
| `parse_to_base64()`                                       | ✅                                        | Utilitária igual                      |
| `normalize_phone_number()` / `is_valid_whatsapp_number()` | ✅                                        | Iguais                                |
| Parâmetro `is_base64`                                     | ✅                                        | Mantido por compat                    |
| Campos `instance_id`, `token`                             | ⚙️ Opcional / legado                     |                                       |
| Base URL API direta                                       | ❌ Não usada — o Manager cuida dos envios |                                       |

> Você pode substituir seu módulo antigo pelo novo `whats77.py` sem alterar chamadas de código.

---

## 🧠 Como Funciona Internamente

1. `Whats77.send_*()` monta um `payload JSON` contendo:

   * `idempotency_key` (gerada automaticamente)
   * `sender_id`, `to`, `text` ou `image_url` ou `document_path`
   * `priority` (`default` por padrão)

2. O payload é enviado para:

   ```
   POST {MANAGER_URL}/enqueue
   ```

3. O Manager:

   * Valida `X-API-Key`
   * Enfileira no Redis
   * O worker processa e dispara via Z-API

---

## 🧾 Resposta de Exemplo do Manager

```json
{
  "status": "queued",
  "idempotency_key": "img:5511999999999:abc123def456",
  "to": "5511999999999",
  "priority": "default"
}
```

---

## 🧰 Dependências

| Biblioteca      | Versão mínima |
| --------------- | ------------- |
| `requests`      | 2.0.0         |
| `python-dotenv` | 0.21.0        |

Instale com:

```bash
pip install requests python-dotenv
```

---

## 🏁 Migração Rápida

1. Substitua seu arquivo antigo `whats77.py` por este novo.
2. Adicione no `.env` as variáveis do Manager:

   ```
   MANAGER_URL=http://localhost:8000
   MANAGER_API_KEY=meu_token_super_seguro
   SENDER_ID=0
   ```
3. Rode seu código existente — nenhuma alteração nas chamadas é necessária.

---
