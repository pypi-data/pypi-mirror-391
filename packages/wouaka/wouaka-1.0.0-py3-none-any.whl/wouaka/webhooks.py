"""
Utilitaires pour la gestion des webhooks Wouaka
"""

import hmac
import hashlib
from typing import Union


def verify_signature(
    payload: Union[str, bytes],
    signature: str,
    webhook_secret: str,
) -> bool:
    """
    Vérifier la signature d'un webhook Wouaka

    Args:
        payload: Corps de la requête webhook (string ou bytes)
        signature: Signature reçue dans le header X-Wouaka-Signature
        webhook_secret: Votre secret webhook (obtenu depuis le dashboard)

    Returns:
        True si la signature est valide, False sinon

    Example:
        >>> from wouaka.webhooks import verify_signature
        >>> 
        >>> @app.route('/webhooks/wouaka', methods=['POST'])
        >>> def handle_webhook():
        ...     payload = request.data
        ...     signature = request.headers.get('X-Wouaka-Signature')
        ...     
        ...     if not verify_signature(payload, signature, WEBHOOK_SECRET):
        ...         return 'Invalid signature', 401
        ...     
        ...     # Traiter le webhook
        ...     return 'OK', 200
    """
    if isinstance(payload, str):
        payload = payload.encode("utf-8")

    # Calculer le HMAC SHA-256
    expected_signature = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Comparer de manière sécurisée (timing-safe)
    return hmac.compare_digest(expected_signature, signature)


def parse_event(payload: Union[str, dict]) -> dict:
    """
    Parser le payload d'un événement webhook

    Args:
        payload: Corps de la requête (JSON string ou dict)

    Returns:
        Dictionnaire avec les détails de l'événement

    Example:
        >>> from wouaka.webhooks import parse_event
        >>> 
        >>> event = parse_event(request.json)
        >>> 
        >>> if event['type'] == 'kyc.verified':
        ...     print(f"KYC vérifié: {event['data']['verification_id']}")
        >>> elif event['type'] == 'evaluation.completed':
        ...     print(f"Évaluation: {event['data']['iea_score']}")
    """
    if isinstance(payload, str):
        import json
        return json.loads(payload)
    return payload


# Types d'événements webhook disponibles
WEBHOOK_EVENTS = {
    # KYC
    "kyc.verified": "Vérification KYC complétée avec succès",
    "kyc.failed": "Vérification KYC échouée",
    
    # IEA
    "evaluation.completed": "Évaluation IEA complétée",
    "evaluation.failed": "Évaluation IEA échouée",
    
    # TrustLink
    "audit.completed": "Audit TrustLink complété",
    "audit.updated": "Audit TrustLink mis à jour",
    
    # Alertes
    "alert.generated": "Alerte système générée",
    "quota.warning": "Avertissement quota (90% consommé)",
    "quota.exceeded": "Quota dépassé",
}
