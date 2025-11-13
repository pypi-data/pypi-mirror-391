"""
Exemple d'utilisation du module TrustLink WouakaAtlas
"""

from wouaka import WouakaClient

# Initialiser le client
client = WouakaClient(
    api_key="wka_live_votre_cle_api",
    environment="production"
)

# ========================================
# Exemple 1: Audit simple d'un projet immobilier
# ========================================

audit = client.trustlink.create_audit(
    project_name="Construction Immeuble R+3 Riviera",
    project_type="real_estate",
    location={
        "latitude": 5.3599,
        "longitude": -4.0083,
        "address": "Riviera 2, Abidjan"
    },
    declared_value=50000000,  # 50 millions FCFA
)

print("🏗️ Audit de projet créé")
print(f"Score de conformité: {audit['compliance_score']}/100")
print(f"Nombre de risques détectés: {len(audit['risks_detected'])}")

# Afficher les risques
if audit['risks_detected']:
    print("\n⚠️ Risques identifiés:")
    for risk in audit['risks_detected']:
        print(f"  - {risk['type']}: {risk['description']} (Gravité: {risk['severity']})")
else:
    print("✅ Aucun risque majeur détecté")

# ========================================
# Exemple 2: Audit avec images satellite
# ========================================

audit_with_satellite = client.trustlink.create_audit(
    project_name="Extension Ferme Avicole",
    project_type="agriculture",
    location={
        "latitude": 5.4520,
        "longitude": -4.0135,
        "address": "Bingerville, Côte d'Ivoire"
    },
    declared_value=15000000,
    satellite_images={
        "before": "./satellite/avant_2022.jpg",
        "after": "./satellite/apres_2025.jpg"
    },
    field_visit_data={
        "visit_date": "2025-01-15",
        "inspector_notes": "Structures conformes, travaux en cours",
        "photos_count": 12
    }
)

print("\n🛰️ Analyse satellite:")
print(f"Changement détecté: {audit_with_satellite['satellite_analysis']['change_detected']}")
print(f"Surface construite: {audit_with_satellite['satellite_analysis']['built_area_sqm']} m²")
print(f"Taux de réalisation: {audit_with_satellite['progress_percentage']}%")

# ========================================
# Exemple 3: Mettre à jour un audit
# ========================================

# Après une visite de terrain, mettre à jour l'audit
updated_audit = client.trustlink.update_audit(
    audit_id=audit['id'],
    field_visit_data={
        "visit_date": "2025-01-20",
        "actual_progress": 75,
        "quality_rating": "good",
        "photos": [
            {"url": "https://...", "description": "Fondations"},
            {"url": "https://...", "description": "Structure béton"},
        ]
    },
    additional_notes="Projet avance selon le planning. Qualité des matériaux conforme."
)

print(f"\n✅ Audit mis à jour")
print(f"Nouveau score: {updated_audit['compliance_score']}/100")

# ========================================
# Exemple 4: Analyse satellite détaillée
# ========================================

satellite_analysis = client.trustlink.get_satellite_analysis(audit_id=audit['id'])

print("\n🌍 Analyse satellite détaillée:")
print(f"Couverture végétale avant: {satellite_analysis['vegetation_before']}%")
print(f"Couverture végétale après: {satellite_analysis['vegetation_after']}%")
print(f"Surfaces imperméabilisées: +{satellite_analysis['impervious_surface_change']}%")
print(f"Détection d'eau à proximité: {satellite_analysis['water_bodies_nearby']}")

# ========================================
# Exemple 5: Obtenir facteurs de risque
# ========================================

risk_factors = client.trustlink.get_risk_factors(audit_id=audit['id'])

print("\n🚨 Facteurs de risque:")
for category, risks in risk_factors.items():
    print(f"\n{category}:")
    for risk in risks:
        severity_emoji = "🔴" if risk['severity'] == "high" else "🟡" if risk['severity'] == "medium" else "🟢"
        print(f"  {severity_emoji} {risk['description']}")
        print(f"     Impact: {risk['impact']}")
        print(f"     Mitigation: {risk['mitigation_strategy']}")

# ========================================
# Exemple 6: Lister tous les audits
# ========================================

audits = client.trustlink.list_audits(
    limit=20,
    project_type="real_estate",
    min_compliance_score=70
)

print(f"\n📋 {audits['total']} audits trouvés")
for audit_item in audits['data']:
    status_emoji = "✅" if audit_item['compliance_score'] >= 80 else "⚠️" if audit_item['compliance_score'] >= 60 else "❌"
    print(f"{status_emoji} {audit_item['project_name']}: {audit_item['compliance_score']}/100")

# ========================================
# Exemple 7: Workflow complet d'audit projet
# ========================================

def complete_project_audit(project_data):
    """Workflow complet: création -> analyse -> mise à jour -> décision"""
    
    # 1. Créer l'audit initial
    print("📝 Étape 1: Création de l'audit")
    audit = client.trustlink.create_audit(**project_data)
    audit_id = audit['id']
    
    # 2. Analyser les données satellite
    print("🛰️ Étape 2: Analyse satellite")
    satellite = client.trustlink.get_satellite_analysis(audit_id=audit_id)
    
    # 3. Obtenir les facteurs de risque
    print("🚨 Étape 3: Évaluation des risques")
    risks = client.trustlink.get_risk_factors(audit_id=audit_id)
    
    # 4. Décision finale
    print("🎯 Étape 4: Décision")
    if audit['compliance_score'] >= 80:
        decision = "APPROUVÉ - Projet conforme, risque faible"
    elif audit['compliance_score'] >= 60:
        decision = "SOUS RÉSERVE - Audit terrain requis, risques modérés"
    else:
        decision = "REFUSÉ - Non-conformités majeures, risque élevé"
    
    return {
        "audit_id": audit_id,
        "score": audit['compliance_score'],
        "decision": decision,
        "satellite_analysis": satellite,
        "risks": risks
    }

# Exemple d'utilisation
project = {
    "project_name": "Centre Commercial Modern Plaza",
    "project_type": "real_estate",
    "location": {"latitude": 5.36, "longitude": -4.01},
    "declared_value": 250000000,
    "satellite_images": {
        "before": "./satellite/avant.jpg",
        "after": "./satellite/apres.jpg"
    }
}

result = complete_project_audit(project)
print(f"\n{'='*50}")
print(f"DÉCISION FINALE: {result['decision']}")
print(f"Score de conformité: {result['score']}/100")
print(f"{'='*50}")
