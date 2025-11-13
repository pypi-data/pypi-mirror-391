"""
Module TrustLink - Audit de projets WouakaAtlas
"""

from typing import Dict, Any, Optional
from ..exceptions import ValidationError


class TrustLinkModule:
    """Module pour les audits TrustLink (WouakaAtlas)"""

    def __init__(self, client):
        self.client = client

    def create_audit(
        self,
        project_name: str,
        project_type: str,
        location: Dict[str, Any],
        declared_value: float,
        satellite_images: Optional[Dict[str, str]] = None,
        field_visit_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Créer un audit de projet TrustLink

        Args:
            project_name: Nom du projet
            project_type: Type de projet ("real_estate", "agriculture", "infrastructure", etc.)
            location: Dictionnaire avec latitude, longitude
            declared_value: Valeur déclarée du projet (FCFA)
            satellite_images: Images satellite avant/après (optionnel)
            field_visit_data: Données de visite terrain (optionnel)
            **kwargs: Paramètres additionnels

        Returns:
            Résultats de l'audit avec score de conformité et risques détectés

        Example:
            >>> audit = client.trustlink.create_audit(
            ...     project_name="Construction Immeuble R+3",
            ...     project_type="real_estate",
            ...     location={"latitude": 5.36, "longitude": -4.01},
            ...     declared_value=50000000,
            ...     satellite_images={
            ...         "before": "/path/to/before.jpg",
            ...         "after": "/path/to/after.jpg"
            ...     }
            ... )
        """
        # Valider les paramètres
        valid_types = ["real_estate", "agriculture", "infrastructure", "equipment", "other"]
        if project_type not in valid_types:
            raise ValidationError(
                f"Type de projet invalide. Valeurs acceptées: {', '.join(valid_types)}"
            )

        if not isinstance(location, dict) or "latitude" not in location or "longitude" not in location:
            raise ValidationError(
                "Location doit contenir au minimum 'latitude' et 'longitude'"
            )

        if declared_value <= 0:
            raise ValidationError("La valeur déclarée doit être positive")

        # Préparer les fichiers si images satellite fournies
        files = None
        if satellite_images:
            files = {}
            try:
                if "before" in satellite_images:
                    with open(satellite_images["before"], "rb") as f:
                        files["satellite_before"] = f.read()
                if "after" in satellite_images:
                    with open(satellite_images["after"], "rb") as f:
                        files["satellite_after"] = f.read()
            except FileNotFoundError as e:
                raise ValidationError(f"Fichier image non trouvé: {e.filename}")

        # Préparer les données
        data = {
            "project_name": project_name,
            "project_type": project_type,
            "location": location,
            "declared_value": declared_value,
            "field_visit_data": field_visit_data or {},
            **kwargs,
        }

        # Effectuer la requête
        response = self.client.post("audit-trustlink", data=data, files=files)
        return response

    def get_audit(self, audit_id: str) -> Dict[str, Any]:
        """
        Récupérer les détails d'un audit TrustLink existant

        Args:
            audit_id: ID de l'audit

        Returns:
            Détails complets de l'audit
        """
        return self.client.get(f"trustlink-audit/{audit_id}")

    def list_audits(
        self,
        limit: int = 50,
        offset: int = 0,
        project_type: Optional[str] = None,
        min_compliance_score: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Lister les audits TrustLink

        Args:
            limit: Nombre maximum de résultats (défaut: 50)
            offset: Décalage pour la pagination (défaut: 0)
            project_type: Filtrer par type de projet (optionnel)
            min_compliance_score: Score de conformité minimum (0-100)

        Returns:
            Liste des audits avec métadonnées de pagination
        """
        params = {"limit": limit, "offset": offset}
        if project_type:
            params["project_type"] = project_type
        if min_compliance_score is not None:
            params["min_compliance_score"] = min_compliance_score

        return self.client.get("trustlink-audits", params=params)

    def update_audit(
        self,
        audit_id: str,
        field_visit_data: Optional[Dict[str, Any]] = None,
        additional_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mettre à jour un audit avec nouvelles données de terrain

        Args:
            audit_id: ID de l'audit
            field_visit_data: Nouvelles données de visite terrain
            additional_notes: Notes additionnelles

        Returns:
            Audit mis à jour
        """
        data = {}
        if field_visit_data:
            data["field_visit_data"] = field_visit_data
        if additional_notes:
            data["additional_notes"] = additional_notes

        return self.client.put(f"trustlink-audit/{audit_id}", data=data)

    def get_satellite_analysis(self, audit_id: str) -> Dict[str, Any]:
        """
        Obtenir l'analyse satellite détaillée d'un audit

        Args:
            audit_id: ID de l'audit

        Returns:
            Analyse satellite avec détection de changements et métriques
        """
        return self.client.get(f"trustlink-satellite-analysis/{audit_id}")

    def get_risk_factors(self, audit_id: str) -> Dict[str, Any]:
        """
        Obtenir les facteurs de risque détectés pour un audit

        Args:
            audit_id: ID de l'audit

        Returns:
            Liste détaillée des risques avec niveaux de gravité
        """
        return self.client.get(f"trustlink-risk-factors/{audit_id}")
