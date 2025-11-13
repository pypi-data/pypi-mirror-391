"""
Client principal du SDK Wouaka
"""

import requests
from typing import Optional, Dict, Any
from .modules import KYCModule, IEAModule, TrustLinkModule
from .exceptions import (
    WouakaAPIError,
    InvalidAPIKeyError,
    QuotaExceededError,
    NetworkError,
)


class WouakaClient:
    """Client principal pour interagir avec l'API Wouaka"""

    # URL de base configurable via variable d'environnement
    DEFAULT_BASE_URL = "https://zepjttggtilxupbzjruj.supabase.co/functions/v1"

    def __init__(
        self,
        api_key: str,
        environment: str = "production",
        timeout: int = 30,
        retry_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialiser le client Wouaka

        Args:
            api_key: Votre clé API Wouaka (commence par wka_)
            environment: "production" ou "sandbox"
            timeout: Timeout des requêtes en secondes (défaut: 30)
            retry_config: Configuration des retries automatiques
        """
        if not api_key or not api_key.startswith("wka_"):
            raise InvalidAPIKeyError("Clé API invalide. Doit commencer par 'wka_'")

        self.api_key = api_key
        self.environment = environment
        
        # Support de la variable d'environnement WOUAKA_API_URL pour configuration flexible
        import os
        self.base_url = os.getenv('WOUAKA_API_URL', self.DEFAULT_BASE_URL)
        self.timeout = timeout

        # Configuration retry par défaut
        self.retry_config = retry_config or {
            "max_retries": 3,
            "backoff_factor": 2,
            "retry_on": [408, 500, 502, 503, 504],
        }

        # Initialiser les modules
        self.kyc = KYCModule(self)
        self.iea = IEAModule(self)
        self.trustlink = TrustLinkModule(self)

    def _get_headers(self) -> Dict[str, str]:
        """Générer les headers pour les requêtes API"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Wouaka-SDK": "python/1.0.0",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Effectuer une requête HTTP avec retry automatique

        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint de l'API
            data: Données JSON à envoyer
            files: Fichiers à uploader
            params: Paramètres query string

        Returns:
            Réponse JSON de l'API

        Raises:
            WouakaAPIError: En cas d'erreur API
            NetworkError: En cas d'erreur réseau
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        # Si on envoie des fichiers, ne pas spécifier Content-Type
        if files:
            headers.pop("Content-Type", None)

        max_retries = self.retry_config["max_retries"]
        backoff_factor = self.retry_config["backoff_factor"]
        retry_on = self.retry_config["retry_on"]

        for attempt in range(max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if not files else None,
                    files=files,
                    params=params,
                    timeout=self.timeout,
                )

                # Vérifier le code de statut
                if response.status_code == 200:
                    return response.json()

                # Erreurs spécifiques
                if response.status_code == 401:
                    raise InvalidAPIKeyError("Clé API invalide ou expirée")

                if response.status_code == 429:
                    error_data = response.json()
                    raise QuotaExceededError(
                        message="Quota API dépassé",
                        quota_limit=error_data.get("quota_limit"),
                        quota_used=error_data.get("quota_used"),
                    )

                # Retry sur certains codes d'erreur
                if response.status_code in retry_on and attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    import time
                    time.sleep(wait_time)
                    continue

                # Erreur générique
                error_message = response.json().get("error", "Erreur inconnue")
                raise WouakaAPIError(
                    message=error_message,
                    status_code=response.status_code,
                    response=response.json(),
                )

            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    import time
                    time.sleep(wait_time)
                    continue
                raise NetworkError("Timeout - le serveur ne répond pas")

            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    import time
                    time.sleep(wait_time)
                    continue
                raise NetworkError("Erreur de connexion réseau")

            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Erreur réseau: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Effectuer une requête GET"""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Effectuer une requête POST"""
        return self._make_request("POST", endpoint, data=data, files=files)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Effectuer une requête PUT"""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Effectuer une requête DELETE"""
        return self._make_request("DELETE", endpoint)
