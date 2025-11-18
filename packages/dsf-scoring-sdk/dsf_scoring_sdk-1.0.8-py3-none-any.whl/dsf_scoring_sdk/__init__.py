# ============================================
# dsf_scoring_sdk/__init__.py
# ============================================
"""SDK de Python para la API de DSF Scoring"""

# La versión aquí DEBE COINCIDIR con la de pyproject.toml
# Sugerí 0.1.0 para el primer despliegue en PyPI.
__version__ = '1.0.8' 
__author__ = 'Jaime Alexander Jimenez'
__email__ = 'contacto@dsfuptech.cloud'

# Importa la clase correcta de client.py
from .client import CreditScoreClient 

# Importa las excepciones
from .exceptions import AccessSDKError, ValidationError, LicenseError, APIError

# No hay 'models.py' en esta versión, así que no se importan

__all__ = [
    'CreditScoreClient',  # Nombre de clase actualizado
    'AccessSDKError',
    'ValidationError',
    'LicenseError',
    'APIError'
]