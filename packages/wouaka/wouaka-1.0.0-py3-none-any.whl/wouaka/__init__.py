"""
Wouaka Python SDK

SDK Python officiel pour l'API Wouaka - Solutions de scoring crédit 
et vérification KYC pour l'Afrique de l'Ouest.
"""

from .client import WouakaClient
from .exceptions import (
    WouakaAPIError,
    InvalidAPIKeyError,
    QuotaExceededError,
    InvalidDocumentError,
    NetworkError,
)

__version__ = "1.0.0"
__all__ = [
    "WouakaClient",
    "WouakaAPIError",
    "InvalidAPIKeyError",
    "QuotaExceededError",
    "InvalidDocumentError",
    "NetworkError",
]
