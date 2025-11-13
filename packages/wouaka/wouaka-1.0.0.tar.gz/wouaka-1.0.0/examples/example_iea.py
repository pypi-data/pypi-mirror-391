"""
Exemple d'utilisation du module IEA WouakaScore
"""

from wouaka import WouakaClient

# Initialiser le client
client = WouakaClient(
    api_key="wka_live_votre_cle_api",
    environment="production"
)

# ========================================
# Exemple 1: Évaluation simple d'une PME
# ========================================

evaluation = client.iea.evaluate(
    business_name="Boulangerie Moderne SARL",
    business_type="sme",
    location={
        "latitude": 5.3599,
        "longitude": -4.0083,
        "address": "Cocody Angré, Abidjan, Côte d'Ivoire"
    }
)

print("📊 Résultats de l'évaluation")
print(f"Score IEA global: {evaluation['iea_score']}/100")
print(f"\nDécomposition:")
print(f"- ISI (Stabilité Individuelle): {evaluation['isi_score']}/100")
print(f"- ISS (Stabilité Satellite): {evaluation['iss_score']}/100")
print(f"- IRM (Résilience au Risque): {evaluation['irm_score']}/100")

print(f"\n🎯 Recommandation: {evaluation['recommendation']}")

# Interpréter la recommandation
if evaluation['recommendation'] == 'approve':
    print("✅ APPROUVER - Faible risque, prêt recommandé")
elif evaluation['recommendation'] == 'review':
    print("⚠️ ÉTUDE APPROFONDIE - Risque moyen, analyse manuelle requise")
else:
    print("❌ REFUSER - Risque élevé, prêt déconseillé")

# ========================================
# Exemple 2: Évaluation avec KYC du gérant
# ========================================

# D'abord, vérifier le KYC du gérant
kyc_result = client.kyc.verify(
    document_image="./gerant_cni.jpg",
    country="CI"
)

# Puis évaluer avec le KYC lié
evaluation = client.iea.evaluate(
    business_name="Commerce Général Afrique",
    business_type="micro",
    location={
        "latitude": 5.3599,
        "longitude": -4.0083,
        "address": "Adjamé, Abidjan"
    },
    manager_info={
        "kyc_verification_id": kyc_result['id'],
        "full_name": kyc_result['data']['full_name'],
        "experience_years": 5
    },
    financial_data={
        "monthly_revenue": 2500000,  # FCFA
        "employees_count": 3
    }
)

print(f"Score IEA: {evaluation['iea_score']}")
print(f"Bonus KYC vérifié: +{evaluation.get('kyc_bonus', 0)} points")

# ========================================
# Exemple 3: Génération de rapport PDF
# ========================================

# Récupérer l'ID de l'évaluation
evaluation_id = evaluation['id']

# Générer le rapport exécutif PDF
pdf_report = client.iea.generate_report(
    evaluation_id=evaluation_id,
    format="pdf",
    include_satellite=True
)

# Sauvegarder le PDF
with open(f"rapport_iea_{evaluation_id}.pdf", "wb") as f:
    f.write(pdf_report)

print(f"✅ Rapport PDF généré: rapport_iea_{evaluation_id}.pdf")

# ========================================
# Exemple 4: Évaluation en lot
# ========================================

businesses = [
    {
        "business_name": "Restaurant Le Palmier",
        "business_type": "micro",
        "location": {"latitude": 5.36, "longitude": -4.01}
    },
    {
        "business_name": "Menuiserie Moderne",
        "business_type": "sme",
        "location": {"latitude": 5.35, "longitude": -3.98}
    },
    {
        "business_name": "Épicerie du Quartier",
        "business_type": "micro",
        "location": {"latitude": 5.34, "longitude": -4.02}
    },
]

batch_results = client.iea.batch_evaluate(businesses)

print("\n📋 Résultats du lot:")
for result in batch_results['results']:
    if result['success']:
        score = result['iea_score']
        name = result['business_name']
        recommendation = result['recommendation']
        
        emoji = "✅" if recommendation == "approve" else "⚠️" if recommendation == "review" else "❌"
        print(f"{emoji} {name}: {score}/100 - {recommendation}")
    else:
        print(f"❌ {result['business_name']}: Erreur - {result['error']}")

# ========================================
# Exemple 5: Récupérer recommandation par score
# ========================================

for score in [85, 65, 45]:
    recommendation = client.iea.get_recommendation(iea_score=score)
    print(f"\nScore {score}/100:")
    print(f"  Décision: {recommendation['decision']}")
    print(f"  Conditions: {recommendation['conditions']}")
    print(f"  Taux d'intérêt suggéré: {recommendation['suggested_interest_rate']}%")
