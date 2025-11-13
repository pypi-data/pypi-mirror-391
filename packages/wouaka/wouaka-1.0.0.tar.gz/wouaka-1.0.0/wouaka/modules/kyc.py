"""
Module KYC - Vérification d'identité WouakaVerify
"""

from typing import Dict, Any, Optional
from ..exceptions import InvalidDocumentError, ValidationError


class KYCModule:
    """Module pour les vérifications KYC (WouakaVerify)"""

    def __init__(self, client):
        self.client = client

    def verify(
        self,
        document_image: str,
        document_type: str = "national_id",
        country: str = "CI",
        selfie_image: Optional[str] = None,
        enable_liveness: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Vérifier un document d'identité

        Args:
            document_image: Chemin vers l'image du document
            document_type: Type de document ("national_id", "passport", "driver_license")
            country: Code pays ISO (CI, SN, BF, ML, etc.)
            selfie_image: Chemin vers le selfie pour vérification faciale (optionnel)
            enable_liveness: Activer la détection de liveness (défaut: True)
            **kwargs: Paramètres additionnels

        Returns:
            Résultat de la vérification avec données extraites et scores

        Raises:
            InvalidDocumentError: Si le document est invalide
            ValidationError: Si les paramètres sont incorrects
        """
        # Valider les paramètres
        valid_types = ["national_id", "passport", "driver_license"]
        if document_type not in valid_types:
            raise ValidationError(
                f"Type de document invalide. Valeurs acceptées: {', '.join(valid_types)}"
            )

        valid_countries = ["CI", "SN", "BF", "ML", "TG", "BJ", "NE", "GW"]
        if country not in valid_countries:
            raise ValidationError(
                f"Code pays invalide. Valeurs acceptées: {', '.join(valid_countries)}"
            )

        # Préparer les fichiers
        files = {}
        try:
            with open(document_image, "rb") as f:
                files["document"] = f.read()

            if selfie_image:
                with open(selfie_image, "rb") as f:
                    files["selfie"] = f.read()
        except FileNotFoundError as e:
            raise ValidationError(f"Fichier non trouvé: {e.filename}")

        # Préparer les données
        data = {
            "document_type": document_type,
            "country": country,
            "enable_liveness": enable_liveness,
            **kwargs,
        }

        # Effectuer la requête
        try:
            response = self.client.post("verify-kyc", data=data, files=files)

            # Si le document est rejeté
            if response.get("status") == "rejected":
                raise InvalidDocumentError(
                    message="Document rejeté",
                    rejection_reason=response.get("rejection_reason"),
                )

            return response

        except Exception as e:
            if hasattr(e, "response") and e.response:
                error_data = e.response
                if error_data.get("is_document_valid") is False:
                    raise InvalidDocumentError(
                        message=error_data.get("error", "Document invalide"),
                        rejection_reason=error_data.get("classification_result"),
                    )
            raise

    def get_verification(self, verification_id: str) -> Dict[str, Any]:
        """
        Récupérer les détails d'une vérification KYC existante

        Args:
            verification_id: ID de la vérification

        Returns:
            Détails complets de la vérification
        """
        return self.client.get(f"kyc-verification/{verification_id}")

    def list_verifications(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lister les vérifications KYC

        Args:
            limit: Nombre maximum de résultats (défaut: 50)
            offset: Décalage pour la pagination (défaut: 0)
            status: Filtrer par statut ("verified", "rejected", "pending")

        Returns:
            Liste des vérifications avec métadonnées de pagination
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        return self.client.get("kyc-verifications", params=params)

    def batch_verify(self, verifications: list) -> Dict[str, Any]:
        """
        Vérifier plusieurs documents en lot

        Args:
            verifications: Liste de dictionnaires contenant les paramètres de vérification

        Returns:
            Résultats des vérifications en lot

        Example:
            >>> verifications = [
            ...     {"document_image": "cni1.jpg", "country": "CI"},
            ...     {"document_image": "cni2.jpg", "country": "SN"},
            ... ]
            >>> results = client.kyc.batch_verify(verifications)
        """
        return self.client.post("kyc-batch-verify", data={"verifications": verifications})
