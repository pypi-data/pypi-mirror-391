"""
Exemple d'utilisation du module KYC WouakaVerify
"""

from wouaka import WouakaClient
from wouaka.exceptions import InvalidDocumentError, QuotaExceededError

# Initialiser le client
client = WouakaClient(
    api_key="wka_live_votre_cle_api",
    environment="production"
)

# ========================================
# Exemple 1: Vérification simple d'une CNI
# ========================================

try:
    result = client.kyc.verify(
        document_image="./documents/cni_ivoirienne.jpg",
        document_type="national_id",
        country="CI"
    )
    
    print("✅ Vérification réussie!")
    print(f"Nom complet: {result['data']['full_name']}")
    print(f"Date de naissance: {result['data']['date_of_birth']}")
    print(f"Numéro document: {result['data']['document_number']}")
    print(f"Score d'authenticité: {result['authenticity_score']}/100")
    print(f"Liveness détectée: {result['liveness_detected']}")

except InvalidDocumentError as e:
    print(f"❌ Document rejeté: {e.rejection_reason}")
    # Raisons possibles:
    # - "not_a_document" (image de fleurs, paysage, etc.)
    # - "screen_capture" (photo d'écran)
    # - "photocopy" (photocopie)
    # - "blurry" (image floue)

except QuotaExceededError as e:
    print(f"❌ Quota dépassé!")
    print(f"Limite: {e.quota_limit}")
    print(f"Utilisé: {e.quota_used}")

# ========================================
# Exemple 2: Vérification avec selfie
# ========================================

result = client.kyc.verify(
    document_image="./documents/cni.jpg",
    document_type="national_id",
    country="SN",
    selfie_image="./documents/selfie.jpg",
    enable_liveness=True
)

if result['face_match_score'] > 80:
    print("✅ Visage correspond au document")
else:
    print("⚠️ Faible correspondance faciale")

# ========================================
# Exemple 3: Récupérer une vérification existante
# ========================================

verification = client.kyc.get_verification("kyc_abc123")
print(f"Statut: {verification['status']}")
print(f"Créée le: {verification['created_at']}")

# ========================================
# Exemple 4: Lister toutes les vérifications
# ========================================

verifications = client.kyc.list_verifications(
    limit=10,
    status="verified"
)

print(f"Total vérifications: {verifications['total']}")
for v in verifications['data']:
    print(f"- {v['data']['full_name']} ({v['country']})")

# ========================================
# Exemple 5: Vérification en lot
# ========================================

batch_data = [
    {
        "document_image": "./docs/cni1.jpg",
        "country": "CI",
        "document_type": "national_id"
    },
    {
        "document_image": "./docs/cni2.jpg",
        "country": "SN",
        "document_type": "national_id"
    },
]

batch_results = client.kyc.batch_verify(batch_data)

for idx, result in enumerate(batch_results['results']):
    if result['success']:
        print(f"✅ Document {idx+1}: {result['data']['full_name']}")
    else:
        print(f"❌ Document {idx+1}: {result['error']}")
