# client.py (Completo y Actualizado)

from __future__ import annotations

import json
import uuid
import logging
import time
from functools import wraps
from typing import Dict, Optional, List, Any
from urllib.parse import urljoin

import requests

# Importa las excepciones actualizadas
from . import __version__
from .exceptions import ValidationError, LicenseError, APIError

logger = logging.getLogger(__name__)


# --- CAMBIO 1: Decorador de reintento actualizado ---
def retry_on_failure(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    Decorador de reintento que usa backoff exponencial y respeta
    el header Retry-After en errores 429.
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
                    # No reintentar errores 4xx (excepto 429)
                    if e.status_code and 400 <= e.status_code < 500 and e.status_code != 429:
                        raise
                    
                    if attempt == max_retries - 1:
                        break # No dormir en el último intento

                    wait_time = delay
                    if e.status_code == 429 and e.retry_after:
                        # Respeta el tiempo de espera del servidor
                        wait_time = e.retry_after
                        logger.warning(f"Attempt {attempt + 1} failed (429 Rate Limit). Retrying in {wait_time}s...")
                    else:
                        # Usa backoff exponencial
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
            
            # Si se agotaron los reintentos, lanzar la última excepción
            raise last_exception or APIError("Max retries exceeded")
        return wrapper
    return decorator


class CreditScoreClient:
    """
    SDK para evaluar credit scoring con aprendizaje adaptativo.
    """
    
    BASE_URL = "https://dsf-scoring-r99cblng2-api-dsfuptech.vercel.app/"  # Tu URL de producción
    ENDPOINT = ""  # Root endpoint
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

        # --- CAMBIO 2: Comentario de advertencia añadido ---
        # ATENCIÓN: esta validación hace una llamada HTTP bloqueante en el constructor.
        if tier != "community" and license_key:
            self._validate_license()

    def _validate_license(self):
        """Valida la licencia haciendo una llamada de prueba"""
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

    @retry_on_failure(max_retries=3)
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """
        Realiza request con idempotencia via X-Request-Id.
        Maneja 429 respetando Retry-After.
        """
        url = urljoin(self.base_url, endpoint)
        
        # Generar request ID único para idempotencia
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

            # --- CAMBIO 3: Capturar Retry-After y pasarlo al APIError ---
            if resp.status_code == 429:
                retry_after = int(resp.headers.get('Retry-After', 60))
                raise APIError(
                    f"Rate limited. Retry after {retry_after} seconds",
                    status_code=429,
                    retry_after=retry_after  # Pasar el valor a la excepción
                )

            # Parsear error
            try:
                err = resp.json()
            except Exception:
                err = {"error": (resp.text or "API error").strip()}

            if resp.status_code == 403:
                raise LicenseError(err.get("error", "License error"))
            
            raise APIError(
                err.get("error", "API error"),
                status_code=resp.status_code
            )

        except requests.Timeout:
            raise APIError("Request timeout")
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}")

    def evaluate(
        self,
        applicant: Dict[str, Any],
        config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evalúa un solicitante de crédito.
        
        Args:
            applicant: Datos del solicitante. Ej:
                {
                    "credit_score": 680,
                    "debt_to_income": 0.35,
                    ...
                }
            
            config: Configuración de features con pesos y criticidad:
                {
                    "credit_score": {
                        "default": 700,
                        "weight": 2.0,
                        "criticality": 2.5
                    },
                    ...
                }
        
        # --- CAMBIO 4: Docstring actualizada ---
        Returns:
            Dict[str, Any]: {
                "decision": "approved" | "denied",
                "score": float,
                "threshold": float,
                "tier": str,
                "metrics": dict  # disponible en licencias premium
            }
        """
        if not isinstance(applicant, dict):
            raise ValidationError("applicant must be a dictionary")
        if not isinstance(config, dict):
            raise ValidationError("config must be a dictionary")

        payload = {
            "applicant": applicant,
            "config": config,
            "tier": self.tier
        }
        
        if self.license_key:
            payload["license_key"] = self.license_key

        return self._make_request(self.ENDPOINT, payload)

    def evaluate_batch(
        self,
        applicants: List[Dict[str, Any]],
        config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evalúa múltiples solicitantes (solo tiers premium).
        
        Args:
            applicants: Lista de diccionarios con datos de solicitantes
            config: Configuración común para todos
        
        Returns:
            {
                "decisions": {0: "approved", 1: "denied", ...},
                "scores": {0: 0.82, 1: 0.54, ...},
                "threshold": 0.65,
                "tier": "professional",
                "metrics": {...} # disponible en licencias premium
            }
        """
        if self.tier == "community":
            raise PermissionError("Batch evaluation requires premium license")
        
        if not isinstance(applicants, list):
            raise ValidationError("applicants must be a list")
        if not isinstance(config, dict):
            raise ValidationError("config must be a dictionary")

        payload = {
            "applicants": applicants,
            "config": config,
            "tier": self.tier,
            "license_key": self.license_key
        }

        return self._make_request(self.ENDPOINT, payload)

    # --- CAMBIO 5: Método get_metrics() eliminado ---

    def close(self):
        """Cierra la sesión HTTP"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# --- CAMBIO 6: Bloque __name__ actualizado ---
if __name__ == "__main__":
    print(
        "Este módulo no debe ejecutarse directamente.\n"
        "Importa el cliente en tu proyecto usando:\n"
        "from dsf_scoring_sdk import CreditScoreClient"
    )

