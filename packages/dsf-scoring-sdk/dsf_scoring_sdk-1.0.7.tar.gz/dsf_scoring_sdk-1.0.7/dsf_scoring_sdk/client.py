# client.py (Versión Final — con Chunking Automático en el SDK)

from __future__ import annotations

import json
import uuid
import logging
import time
import re
from functools import wraps
from typing import Dict, Optional, List, Any
from urllib.parse import urljoin

import requests

from . import __version__
from .exceptions import ValidationError, LicenseError, APIError

logger = logging.getLogger(__name__)


# =====================================================
#   DECORADOR DE REINTENTO (BACKOFF + RETRY-AFTER)
# =====================================================
def retry_on_failure(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    Decorador de reintento que usa backoff exponencial y respeta
    Retry-After cuando la API responde 429.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = backoff_factor
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except APIError as e:
                    last_exception = e

                    if e.status_code and 400 <= e.status_code < 500 and e.status_code != 429:
                        raise

                    if attempt == max_retries - 1:
                        break

                    wait_time = delay

                    if e.status_code == 429 and e.retry_after:
                        wait_time = e.retry_after
                        logger.warning(f"Attempt {attempt + 1} failed (429). Retrying in {wait_time}s...")
                    else:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        delay *= 2

                    time.sleep(wait_time)

                except requests.RequestException as e:
                    last_exception = APIError(f"Request failed: {e}")

                    if attempt == max_retries - 1:
                        break

                    logger.warning(f"Network error on attempt {attempt + 1}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2

            raise last_exception or APIError("Max retries exceeded")

        return wrapper

    return decorator


# =====================================================
#                CLIENTE PRINCIPAL
# =====================================================
class CreditScoreClient:
    """
    SDK para evaluar credit scoring con soporte para batching
    y rate-limit handling.
    """

    BASE_URL = "https://dsf-scoring-ptgxvdsz9-api-dsfuptech.vercel.app/"
    ENDPOINT = ""
    TIERS = {"community", "professional", "enterprise"}

    def __init__(
        self,
        api_key: str,
        license_key: Optional[str] = None,
        tier: str = "community",
        base_url: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        if not api_key:
            raise ValidationError("api_key is required")

        if tier not in self.TIERS:
            raise ValidationError(f"Invalid tier '{tier}'. Must be one of: {self.TIERS}")

        self.api_key = api_key
        self.license_key = license_key
        self.tier = tier
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"CreditScore-SDK-Python/{__version__}",
            "X-Api-Key": self.api_key,
        })

        # ----------------------------------------
        # VALIDACIÓN ESTRICTa DEL FORMATO DE LICENCIA
        # Solo para tiers premium
        # ----------------------------------------
        if tier != "community" and license_key:
            import re
            license_regex = re.compile(r'^[A-Z0-9-]{25}$')

            if not license_regex.match(license_key):
                raise ValidationError(
                    "The license_key format is invalid. Must be 25 uppercase alphanumeric characters and hyphens."
                )

            # Validación remota (Supabase/Redis)
            self._validate_license()

    # -------------------------------------------------
    #      VALIDACIÓN DE LICENCIA INICIAL
    # -------------------------------------------------
    def _validate_license(self):
        try:
            response = self._make_request(self.ENDPOINT, {
                "applicant": {},
                "config": {"test": {"default": 1, "weight": 1.0}},
                "tier": self.tier,
                "license_key": self.license_key,
            })
            if not response.get("tier"):
                raise LicenseError("License validation failed")
        except APIError as e:
            if e.status_code == 403:
                raise LicenseError(f"Invalid license: {e.message}")
            raise

    # -------------------------------------------------
    #      REQUEST CON RETRY + RETRY-AFTER
    # -------------------------------------------------
    @retry_on_failure(max_retries=3)
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """
        Maneja idempotencia con X-Request-Id y rate limits.
        """
        url = urljoin(self.base_url, endpoint)
        headers = {"X-Request-Id": str(uuid.uuid4())}

        try:
            resp = self.session.post(
                url,
                json=data,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            if resp.status_code == 200:
                try:
                    return resp.json()
                except json.JSONDecodeError:
                    raise APIError("Invalid JSON response from server", status_code=200)

            # 429: Rate Limit → Respeta Retry-After
            if resp.status_code == 429:
                retry_after = int(resp.headers.get('Retry-After', 60))
                raise APIError(
                    f"Rate limited. Retry after {retry_after} seconds",
                    status_code=429,
                    retry_after=retry_after
                )

            # Otros errores
            try:
                err = resp.json()
            except Exception:
                err = {"error": resp.text.strip()}

            if resp.status_code == 403:
                raise LicenseError(err.get("error", "License error"))

            raise APIError(err.get("error", "API error"), status_code=resp.status_code)

        except requests.Timeout:
            raise APIError("Request timeout")
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}")

    # -------------------------------------------------
    #                EVALUACIÓN SIMPLE
    # -------------------------------------------------
    def evaluate(self, applicant: Dict[str, Any], config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(applicant, dict):
            raise ValidationError("applicant must be a dictionary")
        if not isinstance(config, dict):
            raise ValidationError("config must be a dictionary")

        payload = {"applicant": applicant, "config": config, "tier": self.tier}

        if self.license_key:
            payload["license_key"] = self.license_key

        return self._make_request(self.ENDPOINT, payload)

    # -------------------------------------------------
    #                EVALUACIÓN POR LOTES
    # -------------------------------------------------
    def evaluate_batch(
        self,
        applicants: List[Dict[str, Any]],
        config: Dict[str, Dict[str, Any]],
        enable_trace: bool = False # <-- AÑADIR NUEVO PARÁMETRO
    ) -> Dict[str, Any]:
        """
        Evalúa N aplicantes. Chunking automático en el SDK.
        Ahora incluye el flag enable_trace para solicitar datos de explicabilidad.
        """
        # VALIDACIONES BÁSICAS
        if self.tier == "community":
            raise PermissionError("Batch evaluation requires premium license")

        if not isinstance(applicants, list):
            raise ValidationError("applicants must be a list")

        if not isinstance(config, dict):
            raise ValidationError("config must be a dictionary")

        # VALIDACIÓN DE TIER PARA TRACES
        if enable_trace and self.tier == 'community':
            raise PermissionError("Explanation traces require premium license")

        CHUNK_SIZE = 10  # seguro para Vercel

        applicant_chunks = self._chunk_list(applicants, CHUNK_SIZE)

        all_scores = {}
        all_decisions = {}
        traces_dict = {} if enable_trace else None # <-- INICIALIZACIÓN CONDICIONAL
        last_threshold = None
        offset = 0

        for chunk in applicant_chunks:

            # 1. CONSTRUCCIÓN DEL PAYLOAD (INCLUYE EL FLAG)
            payload = {
                "applicants": chunk,
                "config": config,
                "tier": self.tier,
                "license_key": self.license_key
            }
            
            # AÑADIR EL FLAG SI ES NECESARIO (Opt-in)
            if enable_trace:
                payload["enable_trace"] = True

            # 2. HACER LA SOLICITUD
            response = self._make_request(self.ENDPOINT, payload)

            # 3. Reconstrucción correcta de índices globales
            for local_key, decision in response["decisions"].items():
                global_index = offset + int(local_key)

                all_decisions[str(global_index)] = decision
                all_scores[str(global_index)] = response["scores"][local_key]

                # RECOLECCIÓN CONDICIONAL DE TRACES
                if enable_trace and "explanation_traces" in response:
                    # El servidor devuelve traces_dict indexado por el offset del chunk
                    traces_dict[str(global_index)] = response["explanation_traces"][local_key] 


            last_threshold = response.get("threshold", last_threshold)

            # Mover offset usando el tamaño REAL del chunk
            offset += len(chunk)

        # 4. DEVOLVER RESPUESTA FINAL
        final_result = {
            "decisions": all_decisions,
            "scores": all_scores,
            "threshold": last_threshold,
            "tier": self.tier
        }

        # INCLUIR TRACES SI SE SOLICITARON
        if enable_trace:
            final_result["explanation_traces"] = traces_dict

        return final_result

    # -------------------------------------------------
    #                HELPER DE CHUNKING
    # -------------------------------------------------
    def _chunk_list(self, data_list, chunk_size):
        return [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]

    # -------------------------------------------------
    #                CONTEXTO
    # -------------------------------------------------
    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    print(
        "Este módulo no debe ejecutarse directamente.\n"
        "Importa el cliente en tu proyecto usando:\n"
        "  from dsf_scoring_sdk import CreditScoreClient"
    )


