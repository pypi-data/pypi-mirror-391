# Wouaka Python SDK

SDK Python officiel pour l'API Wouaka - Solutions de scoring crédit et vérification KYC pour l'Afrique de l'Ouest.

## Installation

```bash
pip install wouaka
```

Ou depuis les sources:

```bash
git clone https://github.com/wouaka/wouaka-python-sdk.git
cd wouaka-python-sdk
pip install -e .
```

## Configuration

```python
from wouaka import WouakaClient

# Initialiser le client avec votre clé API
client = WouakaClient(
    api_key="wka_live_votre_cle_api",
    environment="production"  # ou "sandbox" pour les tests
)
```

## Fonctionnalités

### 1. Vérification KYC (WouakaVerify)

Vérifiez l'identité des clients avec détection de liveness et OCR intelligent.

```python
# Vérifier un document d'identité
result = client.kyc.verify(
    document_image="/path/to/cni.jpg",
    document_type="national_id",
    country="CI"  # Côte d'Ivoire
)

print(f"Statut: {result['status']}")
print(f"Nom: {result['data']['full_name']}")
print(f"Score d'authenticité: {result['authenticity_score']}")
```

### 2. Évaluation IEA (WouakaScore)

Calculez l'Indice d'Évaluabilité Africain pour évaluer le risque de crédit.

```python
# Évaluer une entreprise
evaluation = client.iea.evaluate(
    business_name="Boulangerie Moderne SARL",
    business_type="sme",
    location={
        "latitude": 5.3599,
        "longitude": -4.0083,
        "address": "Cocody Angré, Abidjan"
    },
    manager_info={
        "kyc_verification_id": "kyc_abc123"  # Optionnel
    }
)

print(f"Score IEA: {evaluation['iea_score']}/100")
print(f"Décision: {evaluation['recommendation']}")
print(f"ISI: {evaluation['isi_score']}")
print(f"ISS: {evaluation['iss_score']}")
print(f"IRM: {evaluation['irm_score']}")
```

### 3. Audit TrustLink (WouakaAtlas)

Auditez des projets avec analyse satellite et données de terrain.

```python
# Créer un audit de projet
audit = client.trustlink.create_audit(
    project_name="Construction Immeuble R+3",
    project_type="real_estate",
    location={
        "latitude": 5.3599,
        "longitude": -4.0083
    },
    declared_value=50000000,  # FCFA
    satellite_images={
        "before": "/path/to/before.jpg",
        "after": "/path/to/after.jpg"
    }
)

print(f"Score de conformité: {audit['compliance_score']}")
print(f"Risques détectés: {audit['risks_detected']}")
```

## Gestion des erreurs

```python
from wouaka.exceptions import (
    WouakaAPIError,
    InvalidAPIKeyError,
    QuotaExceededError,
    InvalidDocumentError
)

try:
    result = client.kyc.verify(document_image="invalid.jpg")
except InvalidDocumentError as e:
    print(f"Document invalide: {e.message}")
except QuotaExceededError as e:
    print(f"Quota épuisé. Limite: {e.quota_limit}")
except WouakaAPIError as e:
    print(f"Erreur API: {e.status_code} - {e.message}")
```

## Webhooks

Recevez des notifications en temps réel pour les événements importants.

```python
from wouaka.webhooks import verify_signature

@app.route('/webhooks/wouaka', methods=['POST'])
def handle_webhook():
    payload = request.data
    signature = request.headers.get('X-Wouaka-Signature')
    
    # Vérifier la signature
    if not verify_signature(payload, signature, webhook_secret):
        return 'Invalid signature', 401
    
    event = request.json
    
    if event['type'] == 'kyc.verified':
        # Traiter la vérification KYC complétée
        print(f"KYC vérifié: {event['data']['verification_id']}")
    
    elif event['type'] == 'evaluation.completed':
        # Traiter l'évaluation IEA complétée
        print(f"IEA complété: {event['data']['evaluation_id']}")
    
    return 'OK', 200
```

## Exemples avancés

### Évaluation en lot

```python
# Évaluer plusieurs entreprises en parallèle
businesses = [
    {"name": "Entreprise A", "location": {...}},
    {"name": "Entreprise B", "location": {...}},
]

results = client.iea.batch_evaluate(businesses)

for result in results:
    print(f"{result['business_name']}: {result['iea_score']}")
```

### Mode offline avec retry automatique

```python
from wouaka import WouakaClient

client = WouakaClient(
    api_key="wka_live_...",
    retry_config={
        "max_retries": 3,
        "backoff_factor": 2,
        "retry_on": [408, 500, 502, 503, 504]
    }
)
```

## Support

- **Documentation**: https://docs.wouaka.com
- **Email**: support@wouaka.com
- **Téléphone**: +225 07 01 23 89 74

## Licence

MIT License - Copyright (c) 2025 Wouaka SAS
