import os
import re
import uuid
import logging
import mimetypes
from base64 import b64encode
from os.path import basename, isfile, splitext
from requests import post
from dotenv import load_dotenv

# Config de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Whats77:
    """
    Adapter drop-in que mantém a MESMA interface do integrador antigo,
    mas agora integra com o Whats77 Manager (POST /enqueue).

    Métodos preservados:
      - send_text(phone_number, message)
      - send_image(phone_number, image_path_or_url, caption=None, view_once=False, is_base64=False)
      - send_audio(phone_number, base64_audio)
      - send_document(phone_number, file_path, document_type='pdf', caption=None)

    Comportamento:
      - Gera idempotency_key automaticamente (uuid4) se você não enviar.
      - Normaliza número antes de enfileirar.
      - Aceita imagem/documento por caminho local, URL (http/https) ou data URI.
      - Header de autenticação: X-API-Key.
    """

    # Regras de telefone (mesmas do legado)
    COUNTRY_CODE = "55"
    EXPECTED_LENGTH_NUMBER = 11
    STATE_NUMBER = "9"
    WHATSAPP_NUMBER_PATTERN = r"^55\d{11}$|^\d{12}$"

    # Endpoints do Manager
    ENQUEUE_PATH = "/enqueue"

    def __init__(
        self,
        instance_id=None,          # legado: ignorado quando MANAGER_URL estiver setado
        token=None,                # legado: ignorado quando MANAGER_URL estiver setado
        security_token=None,       # legado: vira fallback de MANAGER_API_KEY se este faltar
        *,
        manager_url: str | None = None,
        manager_api_key: str | None = None,
        sender_id: str | None = None,
        timeout: int = 30,
        default_priority: str = "default",
    ):
        load_dotenv()

        # Preferência por MANAGER_*; mantém compat com construtor antigo
        self.manager_url = manager_url or os.getenv("MANAGER_URL")
        self.api_key = manager_api_key or os.getenv("MANAGER_API_KEY") or security_token or os.getenv("SECURITY_TOKEN")
        self.sender_id = sender_id or os.getenv("SENDER_ID", "0")
        self.timeout = timeout
        self.default_priority = default_priority

        # Legado (não usados se manager_url estiver presente; mantidos por compat)
        self.instance_id = instance_id or os.getenv("INSTANCE_ID")
        self.token = token or os.getenv("TOKEN")

        if not self.manager_url:
            raise ValueError("MANAGER_URL não configurada (defina MANAGER_URL ou passe manager_url=).")
        if not self.api_key:
            raise ValueError("MANAGER_API_KEY não configurada (defina MANAGER_API_KEY ou passe manager_api_key=).")

        self.enqueue_url = self.manager_url.rstrip("/") + self.ENQUEUE_PATH
        logger.info(f"[Whats77] usando Manager em: {self.enqueue_url}")

    # ==========================
    # Helpers de telefone
    # ==========================

    @staticmethod
    def normalize_phone_number(number: str) -> str:
        clean_number = re.sub(r"\D", "", number or "")
        if len(clean_number) == 10:
            clean_number = Whats77.STATE_NUMBER + clean_number
        elif (
            len(clean_number) == Whats77.EXPECTED_LENGTH_NUMBER
            and not clean_number.startswith(Whats77.COUNTRY_CODE)
        ):
            clean_number = Whats77.COUNTRY_CODE + clean_number
        return clean_number

    @staticmethod
    def is_valid_whatsapp_number(number: str) -> bool:
        return re.match(Whats77.WHATSAPP_NUMBER_PATTERN, number or "") is not None

    # ==========================
    # Helpers de arquivo/imagem
    # ==========================

    @staticmethod
    def parse_to_base64(file_path: str) -> str:
        with open(file_path, "rb") as f:
            return b64encode(f.read()).decode()

    @staticmethod
    def _guess_image_mime_from_path(path: str) -> str:
        mime, _ = mimetypes.guess_type(path)
        if mime and mime.startswith("image/"):
            return mime
        ext = splitext(path)[1].lstrip(".").lower()
        if ext == "jpg":
            return "image/jpeg"
        if ext:
            return f"image/{ext}"
        return "image/jpeg"

    @staticmethod
    def _coerce_image_field(image_path_or_url: str, is_base64_flag: bool = False) -> str:
        """
        Retorna o campo 'image_url' aceito pelo Manager:
        - Se começar com data:image/... -> retorna como está (data URI)
        - Se começar com http(s)://    -> retorna como está (URL)
        - Caso contrário, trata como arquivo local e converte para data URI
        - Compat: se is_base64_flag=True (assinatura antiga), também converte arquivo local para data URI
        """
        if not image_path_or_url:
            raise ValueError("Parâmetro de imagem vazio.")

        val = image_path_or_url.strip()
        low = val.lower()

        # Já é data URI
        if low.startswith("data:image/"):
            return val

        # É URL http/https
        if low.startswith("http://") or low.startswith("https://"):
            return val

        # is_base64 legado OU caminho local detectado ⇒ converte para data URI
        if isfile(val):
            mime = Whats77._guess_image_mime_from_path(val)
            b64 = Whats77.parse_to_base64(val)
            return f"data:{mime};base64,{b64}"

        if is_base64_flag:
            # manter compat: quem marcava is_base64=True espera que caminho inválido estoure
            raise FileNotFoundError(f"Arquivo de imagem não encontrado: {val}")

        # Se não for URL/data e o arquivo não existir, ainda assim deixar como veio
        # (o Manager/worker poderá rejeitar/ajustar conforme a pipeline)
        return val

    @staticmethod
    def _coerce_document_field(file_path_or_datauri: str, document_type: str | None) -> tuple[str, str, str]:
        """
        Retorna (doc_field, file_name, resolved_doc_type) para o Manager.
        Aceita:
        - data:application/<type>;base64,...
        - caminho local (converte e infere type se não vier)
        """
        if not file_path_or_datauri:
            raise ValueError("Parâmetro de documento vazio.")

        val = file_path_or_datauri.strip()
        low = val.lower()

        if low.startswith("data:application/"):
            # tenta extrair tipo
            try:
                header = low.split(";")[0]  # data:application/pdf
                doc_type = header.split("/")[1]
            except Exception:
                doc_type = document_type or "pdf"
            file_name = "document." + (doc_type or "pdf")
            return val, file_name, (doc_type or "pdf")

        if not isfile(val):
            # Deixa passar como veio; o worker decidirá (ou estoura erro mais adiante)
            file_name = basename(val)
            doc_type = document_type or (splitext(val)[1].lstrip(".").lower() or "pdf")
            return val, file_name, doc_type

        # arquivo local ⇒ para data URI
        file_name = basename(val)
        if not document_type:
            mime, _ = mimetypes.guess_type(val)
            if mime and mime.startswith("application/"):
                document_type = mime.split("/")[1]
            else:
                ext = splitext(val)[1].lstrip(".").lower()
                document_type = ext or "pdf"

        with open(val, "rb") as f:
            encoded = b64encode(f.read()).decode()

        data_uri = f"data:application/{document_type};base64,{encoded}"
        return data_uri, file_name, document_type

    # ==========================
    # Métodos públicos (mesma assinatura)
    # ==========================

    def send_text(self, phone_number: str, message: str) -> None:
        phone = self.normalize_phone_number(phone_number)
        if not self.is_valid_whatsapp_number(phone):
            raise ValueError(f"Número inválido: {phone_number}")

        payload = {
            "idempotency_key": self._gen_idem_key("text", phone, message),
            "sender_id": str(self.sender_id),
            "to": phone,
            "text": message,
            "priority": self.default_priority,
        }
        self._enqueue(payload)

    def send_audio(self, phone_number: str, base64_audio: str) -> None:
        phone = self.normalize_phone_number(phone_number)
        if not self.is_valid_whatsapp_number(phone):
            raise ValueError(f"Número inválido: {phone_number}")

        payload = {
            "idempotency_key": self._gen_idem_key("audio", phone, base64_audio[:32]),
            "sender_id": str(self.sender_id),
            "to": phone,
            "audio_base64": base64_audio,
            "priority": self.default_priority,
        }
        self._enqueue(payload)

    def send_document(self, phone_number: str, file_path: str, document_type: str = "pdf", caption: str = None) -> None:
        """
        Compat total:
        - aceita caminho local, data URI, ou até um identificador remoto (worker decidirá)
        - converte caminho local para data URI para reduzir atrito
        """
        phone = self.normalize_phone_number(phone_number)
        if not self.is_valid_whatsapp_number(phone):
            raise ValueError(f"Número inválido: {phone_number}")

        doc_field, file_name, doc_type = self._coerce_document_field(file_path, document_type)

        payload = {
            "idempotency_key": self._gen_idem_key("doc", phone, file_name),
            "sender_id": str(self.sender_id),
            "to": phone,
            "document_path": doc_field,     # Manager usa 'document_path' (string flexível)
            "document_type": doc_type,
            "caption": caption,
            "priority": self.default_priority,
        }
        self._enqueue(payload)

    def send_image(self, phone_number: str, image_path_or_url: str, caption: str = None, view_once: bool = False, is_base64: bool = False) -> None:
        """
        Compat total com assinatura antiga:
        - URL/data URI passa direto
        - Caminho local vira data URI (ou erro se is_base64=True e arquivo não existir)
        - 'view_once' é ignorado pelo Manager (sem quebra de compat)
        """
        phone = self.normalize_phone_number(phone_number)
        if not self.is_valid_whatsapp_number(phone):
            raise ValueError(f"Número inválido: {phone_number}")

        image_field = self._coerce_image_field(image_path_or_url, is_base64_flag=is_base64)

        payload = {
            "idempotency_key": self._gen_idem_key("img", phone, image_field[:48]),
            "sender_id": str(self.sender_id),
            "to": phone,
            "image_url": image_field,       # Manager usa 'image_url' como string flexível
            "image_caption": caption,
            "priority": self.default_priority,
        }
        self._enqueue(payload)

    # ==========================
    # HTTP para o Manager
    # ==========================

    def _enqueue(self, payload: dict) -> None:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }
        try:
            resp = post(self.enqueue_url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            logger.info(f"[Manager] enfileirado {payload.get('to')} ({payload.get('idempotency_key')}) {resp.status_code}: {data}")
        except Exception as e:
            logger.error(f"[Manager] erro ao enfileirar {payload.get('to')}: {e}")
            raise

    # ==========================
    # Idempotência
    # ==========================

    @staticmethod
    def _gen_idem_key(kind: str, phone: str, seed: str) -> str:
        """
        Gera uma idempotency_key simples e única.
        Mantemos o formato com prefixo para facilitar debug em DLQ/metrics.
        """
        return f"{kind}:{phone}:{uuid.uuid4().hex[:12]}"
