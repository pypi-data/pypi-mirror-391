"""
Module IEA - Évaluation du risque crédit WouakaScore
"""

from typing import Dict, Any, Optional, List
from ..exceptions import ValidationError


class IEAModule:
    """Module pour les évaluations IEA (WouakaScore)"""

    def __init__(self, client):
        self.client = client

    def evaluate(
        self,
        business_name: str,
        business_type: str,
        location: Dict[str, Any],
        manager_info: Optional[Dict[str, Any]] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Évaluer une entreprise avec l'Indice d'Évaluabilité Africain

        Args:
            business_name: Nom de l'entreprise
            business_type: Type d'entreprise ("sme", "micro", "individual", "corporate")
            location: Dictionnaire avec latitude, longitude et adresse
            manager_info: Informations sur le gérant (optionnel)
            financial_data: Données financières (chiffre d'affaires, etc.) (optionnel)
            **kwargs: Paramètres additionnels

        Returns:
            Évaluation complète avec scores ISI, ISS, IRM et recommandation

        Raises:
            ValidationError: Si les paramètres sont incorrects

        Example:
            >>> evaluation = client.iea.evaluate(
            ...     business_name="Boulangerie Moderne",
            ...     business_type="sme",
            ...     location={
            ...         "latitude": 5.3599,
            ...         "longitude": -4.0083,
            ...         "address": "Cocody Angré, Abidjan"
            ...     },
            ...     manager_info={
            ...         "kyc_verification_id": "kyc_abc123"
            ...     }
            ... )
        """
        # Valider les paramètres
        valid_types = ["sme", "micro", "individual", "corporate"]
        if business_type not in valid_types:
            raise ValidationError(
                f"Type d'entreprise invalide. Valeurs acceptées: {', '.join(valid_types)}"
            )

        if not isinstance(location, dict) or "latitude" not in location or "longitude" not in location:
            raise ValidationError(
                "Location doit contenir au minimum 'latitude' et 'longitude'"
            )

        # Préparer les données
        data = {
            "business_name": business_name,
            "business_type": business_type,
            "location": location,
            "manager_info": manager_info or {},
            "financial_data": financial_data or {},
            **kwargs,
        }

        # Effectuer la requête
        response = self.client.post("iea-orchestrator", data=data)
        return response

    def get_evaluation(self, evaluation_id: str) -> Dict[str, Any]:
        """
        Récupérer les détails d'une évaluation IEA existante

        Args:
            evaluation_id: ID de l'évaluation

        Returns:
            Détails complets de l'évaluation
        """
        return self.client.get(f"iea-evaluation/{evaluation_id}")

    def list_evaluations(
        self,
        limit: int = 50,
        offset: int = 0,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lister les évaluations IEA

        Args:
            limit: Nombre maximum de résultats (défaut: 50)
            offset: Décalage pour la pagination (défaut: 0)
            min_score: Score IEA minimum pour filtrage (0-100)
            max_score: Score IEA maximum pour filtrage (0-100)

        Returns:
            Liste des évaluations avec métadonnées de pagination
        """
        params = {"limit": limit, "offset": offset}
        if min_score is not None:
            params["min_score"] = min_score
        if max_score is not None:
            params["max_score"] = max_score

        return self.client.get("iea-evaluations", params=params)

    def batch_evaluate(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Évaluer plusieurs entreprises en lot

        Args:
            evaluations: Liste de dictionnaires contenant les paramètres d'évaluation

        Returns:
            Résultats des évaluations en lot

        Example:
            >>> businesses = [
            ...     {
            ...         "business_name": "Entreprise A",
            ...         "business_type": "sme",
            ...         "location": {"latitude": 5.36, "longitude": -4.01}
            ...     },
            ...     {
            ...         "business_name": "Entreprise B",
            ...         "business_type": "micro",
            ...         "location": {"latitude": 14.68, "longitude": -17.45}
            ...     }
            ... ]
            >>> results = client.iea.batch_evaluate(businesses)
        """
        return self.client.post("iea-batch-evaluate", data={"evaluations": evaluations})

    def generate_report(
        self,
        evaluation_id: str,
        format: str = "pdf",
        include_satellite: bool = True,
    ) -> bytes:
        """
        Générer un rapport d'évaluation

        Args:
            evaluation_id: ID de l'évaluation
            format: Format du rapport ("pdf", "json")
            include_satellite: Inclure les images satellite (défaut: True)

        Returns:
            Contenu du rapport (PDF bytes ou JSON)
        """
        params = {
            "format": format,
            "include_satellite": include_satellite,
        }
        response = self.client.get(f"iea-report/{evaluation_id}", params=params)

        if format == "pdf":
            return response  # Binary content
        return response  # JSON content

    def get_recommendation(self, iea_score: int) -> Dict[str, Any]:
        """
        Obtenir une recommandation de décision basée sur un score IEA

        Args:
            iea_score: Score IEA (0-100)

        Returns:
            Recommandation avec décision, conditions et justifications

        Example:
            >>> recommendation = client.iea.get_recommendation(iea_score=72)
            >>> print(recommendation['decision'])  # "approve" ou "review" ou "reject"
        """
        if not 0 <= iea_score <= 100:
            raise ValidationError("Le score IEA doit être entre 0 et 100")

        return self.client.get(f"iea-recommendation/{iea_score}")
