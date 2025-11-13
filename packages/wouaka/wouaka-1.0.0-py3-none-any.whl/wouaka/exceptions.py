"""
Exceptions personnalisées du SDK Wouaka
"""

from typing import Optional, Dict, Any


class WouakaAPIError(Exception):
    """Exception de base pour toutes les erreurs API Wouaka"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class InvalidAPIKeyError(WouakaAPIError):
    """Exception levée quand la clé API est invalide ou expirée"""

    def __init__(self, message: str = "Clé API invalide ou expirée"):
        super().__init__(message, status_code=401)


class QuotaExceededError(WouakaAPIError):
    """Exception levée quand le quota API est dépassé"""

    def __init__(
        self,
        message: str = "Quota API dépassé",
        quota_limit: Optional[int] = None,
        quota_used: Optional[int] = None,
    ):
        self.quota_limit = quota_limit
        self.quota_used = quota_used
        super().__init__(message, status_code=429)


class InvalidDocumentError(WouakaAPIError):
    """Exception levée quand un document est invalide (KYC)"""

    def __init__(
        self,
        message: str = "Document invalide",
        rejection_reason: Optional[str] = None,
    ):
        self.rejection_reason = rejection_reason
        super().__init__(message, status_code=400)


class NetworkError(WouakaAPIError):
    """Exception levée en cas d'erreur réseau"""

    def __init__(self, message: str = "Erreur réseau"):
        super().__init__(message)


class ValidationError(WouakaAPIError):
    """Exception levée en cas d'erreur de validation des paramètres"""

    def __init__(self, message: str = "Erreur de validation"):
        super().__init__(message, status_code=400)
