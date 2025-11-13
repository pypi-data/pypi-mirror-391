"""
Exemple d'utilisation des webhooks Wouaka avec Flask
"""

from flask import Flask, request, jsonify
from wouaka.webhooks import verify_signature, parse_event, WEBHOOK_EVENTS

app = Flask(__name__)

# Secret webhook obtenu depuis le dashboard Wouaka
WEBHOOK_SECRET = "whsec_votre_secret_webhook"

@app.route('/webhooks/wouaka', methods=['POST'])
def handle_wouaka_webhook():
    """
    Endpoint pour recevoir les webhooks Wouaka
    """
    
    # 1. Récupérer le payload et la signature
    payload = request.data
    signature = request.headers.get('X-Wouaka-Signature')
    
    if not signature:
        return jsonify({"error": "Missing signature"}), 401
    
    # 2. Vérifier la signature
    if not verify_signature(payload, signature, WEBHOOK_SECRET):
        print("❌ Signature invalide - possible tentative de falsification")
        return jsonify({"error": "Invalid signature"}), 401
    
    # 3. Parser l'événement
    event = parse_event(request.json)
    event_type = event.get('type')
    event_data = event.get('data', {})
    
    print(f"✅ Webhook reçu: {event_type}")
    
    # 4. Traiter selon le type d'événement
    
    # === Événements KYC ===
    if event_type == 'kyc.verified':
        handle_kyc_verified(event_data)
    
    elif event_type == 'kyc.failed':
        handle_kyc_failed(event_data)
    
    # === Événements IEA ===
    elif event_type == 'evaluation.completed':
        handle_evaluation_completed(event_data)
    
    elif event_type == 'evaluation.failed':
        handle_evaluation_failed(event_data)
    
    # === Événements TrustLink ===
    elif event_type == 'audit.completed':
        handle_audit_completed(event_data)
    
    elif event_type == 'audit.updated':
        handle_audit_updated(event_data)
    
    # === Événements système ===
    elif event_type == 'quota.warning':
        handle_quota_warning(event_data)
    
    elif event_type == 'quota.exceeded':
        handle_quota_exceeded(event_data)
    
    elif event_type == 'alert.generated':
        handle_alert_generated(event_data)
    
    else:
        print(f"⚠️ Type d'événement inconnu: {event_type}")
    
    return jsonify({"status": "received"}), 200


def handle_kyc_verified(data):
    """Traiter une vérification KYC réussie"""
    verification_id = data.get('verification_id')
    full_name = data.get('full_name')
    authenticity_score = data.get('authenticity_score')
    
    print(f"✅ KYC vérifié: {full_name}")
    print(f"   ID: {verification_id}")
    print(f"   Score authenticité: {authenticity_score}/100")
    
    # Logique métier: activer le compte client, envoyer email, etc.
    # activate_customer_account(verification_id)
    # send_welcome_email(full_name)


def handle_kyc_failed(data):
    """Traiter une vérification KYC échouée"""
    verification_id = data.get('verification_id')
    rejection_reason = data.get('rejection_reason')
    
    print(f"❌ KYC rejeté: {verification_id}")
    print(f"   Raison: {rejection_reason}")
    
    # Notifier le client de soumettre un nouveau document
    # send_kyc_rejection_email(verification_id, rejection_reason)


def handle_evaluation_completed(data):
    """Traiter une évaluation IEA complétée"""
    evaluation_id = data.get('evaluation_id')
    business_name = data.get('business_name')
    iea_score = data.get('iea_score')
    recommendation = data.get('recommendation')
    
    print(f"📊 Évaluation complétée: {business_name}")
    print(f"   Score IEA: {iea_score}/100")
    print(f"   Recommandation: {recommendation}")
    
    # Logique métier selon la recommandation
    if recommendation == 'approve':
        print("   ✅ Prêt approuvé automatiquement")
        # auto_approve_loan(evaluation_id)
    elif recommendation == 'review':
        print("   ⚠️ Envoi pour revue manuelle")
        # send_to_credit_committee(evaluation_id)
    else:
        print("   ❌ Prêt refusé automatiquement")
        # auto_reject_loan(evaluation_id)


def handle_evaluation_failed(data):
    """Traiter une évaluation IEA échouée"""
    evaluation_id = data.get('evaluation_id')
    error = data.get('error')
    
    print(f"❌ Évaluation échouée: {evaluation_id}")
    print(f"   Erreur: {error}")
    
    # Notifier l'équipe technique
    # send_error_notification_to_tech_team(error)


def handle_audit_completed(data):
    """Traiter un audit TrustLink complété"""
    audit_id = data.get('audit_id')
    project_name = data.get('project_name')
    compliance_score = data.get('compliance_score')
    risks_count = data.get('risks_count', 0)
    
    print(f"🏗️ Audit complété: {project_name}")
    print(f"   Score conformité: {compliance_score}/100")
    print(f"   Risques détectés: {risks_count}")
    
    # Décision de déblocage de fonds
    if compliance_score >= 80 and risks_count == 0:
        print("   ✅ Déblocage tranche suivante approuvé")
        # release_next_payment_tranche(audit_id)
    else:
        print("   ⚠️ Visite terrain requise avant déblocage")
        # schedule_field_visit(audit_id)


def handle_audit_updated(data):
    """Traiter une mise à jour d'audit TrustLink"""
    audit_id = data.get('audit_id')
    updated_fields = data.get('updated_fields', [])
    
    print(f"🔄 Audit mis à jour: {audit_id}")
    print(f"   Champs modifiés: {', '.join(updated_fields)}")
    
    # Notifier les parties prenantes
    # notify_stakeholders_of_update(audit_id)


def handle_quota_warning(data):
    """Traiter un avertissement de quota (90% consommé)"""
    quota_type = data.get('quota_type')
    quota_used = data.get('quota_used')
    quota_limit = data.get('quota_limit')
    percentage = (quota_used / quota_limit) * 100
    
    print(f"⚠️ Avertissement quota {quota_type}")
    print(f"   Utilisé: {quota_used}/{quota_limit} ({percentage:.1f}%)")
    
    # Envoyer notification aux admins
    # send_quota_warning_email(quota_type, quota_used, quota_limit)


def handle_quota_exceeded(data):
    """Traiter un dépassement de quota"""
    quota_type = data.get('quota_type')
    
    print(f"🚨 QUOTA DÉPASSÉ: {quota_type}")
    print("   Les requêtes seront bloquées jusqu'au renouvellement")
    
    # Notification urgente + désactiver features temporairement
    # send_urgent_quota_exceeded_alert()
    # temporarily_disable_api_access()


def handle_alert_generated(data):
    """Traiter une alerte système générée"""
    alert_type = data.get('alert_type')
    severity = data.get('severity')
    message = data.get('message')
    
    severity_emoji = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "🔵"
    
    print(f"{severity_emoji} Alerte système: {alert_type}")
    print(f"   Sévérité: {severity}")
    print(f"   Message: {message}")
    
    if severity == "critical":
        # Notifier immédiatement l'équipe technique
        # send_sms_to_oncall_engineer(message)
        pass


# ========================================
# Endpoint pour lister les types d'événements disponibles
# ========================================

@app.route('/webhooks/events', methods=['GET'])
def list_webhook_events():
    """Lister tous les types d'événements webhook Wouaka"""
    return jsonify({
        "webhook_events": [
            {"type": event_type, "description": description}
            for event_type, description in WEBHOOK_EVENTS.items()
        ]
    })


if __name__ == '__main__':
    print("🚀 Serveur webhook Wouaka démarré sur http://localhost:5000")
    print("\nÉvénements supportés:")
    for event_type, description in WEBHOOK_EVENTS.items():
        print(f"  - {event_type}: {description}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
