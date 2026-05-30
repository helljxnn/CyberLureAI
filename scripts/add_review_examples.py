"""Generate borderline review-class examples and append to external datasets."""
from __future__ import annotations

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
URL_FILE = PROJECT_ROOT / "data" / "external" / "url_real.csv"
MSG_FILE = PROJECT_ROOT / "data" / "external" / "message_real.csv"

URL_REVIEW_EXAMPLES = [
    # HTTP + legitimate-looking domain (insecure but not clearly phishing)
    ("review_http_personal", "http://www.johnsmith.com/contact", ""),
    ("review_http_business", "http://www.acmecorp.co/services/login", ""),
    ("review_http_portfolio", "http://www.maria-design.com/projects", ""),
    ("review_http_local", "http://www.tiendabogota.com/catalogo", ""),
    ("review_http_catalog", "http://www.catalogo-online.com/productos", ""),
    ("review_http_event", "http://www.congresomedellin.com/registro", ""),
    ("review_http_gallery", "http://www.fotografia-arte.com/galeria", ""),
    ("review_http_blog", "http://www.blog-tecnologia.com/articulo", ""),
    ("review_http_health", "http://www.clinica-familiar.com/citas", ""),
    ("review_http_edu", "http://www.cursos-virtuales.com/matricula", ""),
    # Link shorteners without clear phishing terms
    ("review_shortener_blog", "https://bit.ly/tech-blog-article-42", ""),
    ("review_shortener_event", "https://tinyurl.com/conf-registration-2026", ""),
    ("review_shortener_form", "https://goo.gl/forms/survey-feedback-q1", ""),
    ("review_shortener_docs", "https://t.co/docs/meeting-notes-may", ""),
    ("review_shortener_calendar", "https://ow.ly/event-calendar-invite", ""),
    ("review_shortener_drive", "https://bit.ly/shared-drive-folder-team", ""),
    ("review_shortener_git", "https://is.gd/repo-docs-readme", ""),
    ("review_shortener_map", "https://tiny.cc/map-office-location", ""),
    ("review_shortener_video", "https://v.gd/tutorial-setup-guide", ""),
    ("review_shortener_support", "https://rb.gy/support-ticket-8821", ""),
    # Many subdomains on legitimate-looking domains
    ("review_deep_corp", "http://mail.internal.corp.example.com/login", ""),
    ("review_deep_portal", "http://portal.admin.secure.example.org/dashboard", ""),
    ("review_deep_api", "http://api.v2.services.example.net/docs", ""),
    ("review_deep_cdn", "http://cdn.assets.static.example.io/bundle", ""),
    ("review_deep_auth", "http://auth.sso.identity.example.co/login", ""),
    ("review_deep_status", "http://status.monitor.uptime.example.com", ""),
    ("review_deep_blog", "http://blog.news.media.example.org/posts", ""),
    ("review_deep_shop", "http://shop.store.catalog.example.shop/products", ""),
    # Hyphens in domain but otherwise normal
    ("review_hyphen_agency", "https://www.digital-marketing-agency.com/portfolio", ""),
    ("review_hyphen_consult", "https://www.it-consulting-firm.com/services", ""),
    ("review_hyphen_realty", "https://www.real-estate-bogota.com/propiedades", ""),
    ("review_hyphen_legal", "https://www.legal-services-online.com/consulta", ""),
    ("review_hyphen_travel", "https://www.travel-agency-colombia.com/paquetes", ""),
    ("review_hyphen_edu", "https://www.online-courses-platform.com/cursos", ""),
    ("review_hyphen_health", "https://www.health-wellness-center.com/citas", ""),
    ("review_hyphen_tech", "https://www.tech-support-help.com/faq", ""),
    # Free hosting platforms (often abused but also legitimate)
    ("review_github_pages", "https://username.github.io/project-docs/", ""),
    ("review_vercel_app", "https://my-app.vercel.app/login", ""),
    ("review_netlify", "https://company-landing.netlify.app/", ""),
    ("review_firebase", "https://project-id.web.app/dashboard", ""),
    ("review_heroku", "https://app-name.herokuapp.com/signup", ""),
    ("review_wix", "https://username.wixsite.com/my-site/services", ""),
    ("review_weebly", "https://business-page.weebly.com/contact", ""),
    ("review_blogspot", "https://tech-insights.blogspot.com/2026/05/review", ""),
    ("review_wordpress", "https://businessblog.wordpress.com/about", ""),
    ("review_glitch", "https://project-demo.glitch.me/status", ""),
    # Single keyword without clear phishing context
    ("review_login_portal", "https://www.colombia-tienda.com/login", ""),
    ("review_account_portal", "https://www.mi-cuenta.co/account/settings", ""),
    ("review_verify_email", "https://www.registro-evento.com/verify-email", ""),
    ("review_signin_page", "https://www.plataforma-edu.com/signin", ""),
    ("review_update_profile", "https://www.comunidad-dev.com/update-profile", ""),
    ("review_confirm_order", "https://www.tienda-virtual.co/confirm-order/8821", ""),
    ("review_billing_info", "https://www.factura-online.com/billing", ""),
    ("review_payment_status", "https://www.servicios-pago.com/payment/status", ""),
    ("review_access_portal", "https://www.gestion-documental.com/access", ""),
    ("review_secure_page", "https://www.consultoria-legal.com/secure/login", ""),
    # Suspicious TLD but normal content path
    ("review_tk_site", "http://www.community-portal.tk/home", ""),
    ("review_ml_site", "http://www.blog-actualidad.ml/noticias", ""),
    ("review_ga_site", "http://www.proyecto-educativo.ga/cursos", ""),
    ("review_cf_site", "http://www.documentacion.cf/descargas", ""),
    ("review_gq_site", "http://www.recursos-gratis.gq/material", ""),
    ("review_xyz_site", "https://www.startup-latam.xyz/about", ""),
    ("review_top_site", "https://www.descargas-rapidas.top/legal", ""),
    ("review_icu_site", "https://www.soporte-tecnico.icu/ayuda", ""),
    # IP-like or numeric domains
    ("review_numeric_subdomain", "http://192-168-1-1.router-setup.com/config", ""),
    ("review_dotted_numeric", "http://www.server-01.hosting-provider.com/status", ""),
    # Long paths with parameters but HTTPS
    ("review_long_path", "https://www.analytics-dashboard.com/reports/summary/2026/may/colombia/export?format=csv&lang=es", ""),
    ("review_query_params", "https://www.event-registration.com/signup?event=tech-conf-2026&track=social&ref=linkedin&coupon=EARLYBIRD", ""),
    ("review_deep_path", "https://www.university-portal.edu/students/courses/engineering/software/syllabus/2026/semester2", ""),
    # Mixed signals: HTTPS + keyword + normal domain
    ("review_secure_login", "https://www.webmail-provider.com/secure-login", ""),
    ("review_verify_account", "https://www.social-network.com/verify-account", ""),
    ("review_update_payment", "https://www.subscription-service.com/update-payment", ""),
    ("review_confirm_identity", "https://www.id-verification.co/confirm-identity", ""),
    ("review_reset_access", "https://www.cloud-storage.com/reset-access", ""),
    ("review_auth_service", "https://www.auth-provider.com/authorize?client_id=app1&redirect=/callback", ""),
    # Hosting platforms with suspicious paths
    ("review_pages_dev", "https://project-demo.pages.dev/admin/login", ""),
    ("review_r2_dev", "https://my-tool.r2.dev/setup/credentials", ""),
    ("review_workers_dev", "https://api-gateway.username.workers.dev/auth", ""),
    ("review_onrender", "https://backend-service.onrender.com/api/login", ""),
    ("review_fly_dev", "https://app-instance.fly.dev/dashboard", ""),
    # Parked or generic-looking domains
    ("review_parked_domain", "http://www.this-domain-is-under-construction.com", ""),
    ("review_redirect_service", "https://go.example-redirect.com/track?id=campaign2026", ""),
    ("review_temporary_site", "https://staging-v2.company-site.com/preview", ""),
]

MSG_REVIEW_EXAMPLES = [
    # Polite requests with links (not urgent)
    ("review_meeting_link", "Hi team, here is the link for our Q2 planning meeting next Tuesday: https://meet.example.com/room/abc123. Please review the agenda beforehand.", ""),
    ("review_document_share", "I have shared the contract draft with you: https://docs.example.com/file/xyz789. Could you review it by Friday? No rush.", ""),
    ("review_event_reminder", "Reminder: Tech conference starts next week. Your registration is confirmed. Access your badge here: https://conf.example.com/badge/1234", ""),
    ("review_form_submission", "Please complete the employee satisfaction survey by end of month: https://forms.example.com/survey/2026-q2. Takes about 5 minutes.", ""),
    ("review_training_link", "Your mandatory compliance training is available at https://training.example.com/courses/compliance-2026. Due by June 15.", ""),
    ("review_support_ticket", "Your support ticket #44221 has been updated. View the response: https://help.example.com/tickets/44221", ""),
    ("review_password_reset", "Someone requested a password reset for your account. If this was you, use this link: https://auth.example.com/reset?token=abc. Link expires in 1 hour.", ""),
    # Delivery notifications
    ("review_delivery_scheduled", "Your package #COL-8821 is scheduled for delivery tomorrow between 9am-12pm. Track here: https://tracking.example.com/COL-8821", ""),
    ("review_courier_contact", "DHL Express: Your shipment from Amazon is out for delivery. Estimated arrival: 2pm today. Confirm receipt: https://dhl.example-delivery.com/confirm", ""),
    ("review_pickup_ready", "Your order is ready for pickup at our Bogota store. Show this code at the counter: PKP-4422. Details: https://store.example.com/order/8821", ""),
    ("review_shipping_update", "Shipping update: Your package has cleared customs. Expected delivery: May 30. Full tracking: https://logistics.example.com/ship/COL-9921", ""),
    ("review_address_verify", "Please verify your shipping address for order #7721 before we dispatch. Missing apartment number. Update: https://shop.example.com/address/7721", ""),
    # Verification/code messages without urgency
    ("review_2fa_code", "Your two-factor authentication code is: 442188. This code expires in 10 minutes. If you did not request this, please ignore.", ""),
    ("review_login_notification", "New sign-in to your account from Bogota, Colombia. If this was you, no action needed. Review activity: https://account.example.com/activity", ""),
    ("review_device_pairing", "A new device is trying to pair with your account. Device: iPhone 16. Approve or deny: https://devices.example.com/pair/8812", ""),
    ("review_security_alert", "Security alert: Password changed on your account. If this was not you, secure your account immediately: https://security.example.com/recover", ""),
    # Invitation/promotional (not malicious but could be abused)
    ("review_webinar_invite", "You are invited to our free webinar: Cybersecurity Best Practices 2026. Register here: https://webinar.example.com/register/cyber2026. Limited spots.", ""),
    ("review_newsletter_promo", "This week only: 20% off premium membership. Use code PREMIUM20 at checkout: https://premium.example.com/upgrade", ""),
    ("review_referral_bonus", "Refer a friend and get $10 credit! Share your link: https://referral.example.com/user/44221", ""),
    ("review_trial_expiry", "Your free trial expires in 3 days. Upgrade to keep your data: https://billing.example.com/upgrade. Cancel anytime.", ""),
    # Professional/business messages
    ("review_invoice_reminder", "Invoice #INV-2026-0442 for $350 is due on June 5. View invoice: https://billing.example.com/invoice/INV-2026-0442", ""),
    ("review_contract_signing", "Please sign the NDA document via DocuSign: https://docusign.example.com/sign/NDA-9921. Required before project kickoff.", ""),
    ("review_payment_receipt", "Payment of $150 received. Receipt: #RCP-8821. View details: https://payments.example.com/receipt/RCP-8821", ""),
    ("review_account_statement", "Your monthly account statement for May 2026 is ready. View: https://banking.example.com/statements/2026-05", ""),
    # Social media notifications
    ("review_connection_request", "Jennifer Lascarro wants to connect with you on LinkedIn. Accept: https://linkedin.example-connect.com/invite/44221", ""),
    ("review_tagged_post", "You were tagged in a post by Carlos Rodriguez. View post: https://social.example.com/post/88219921", ""),
    ("review_message_request", "You have a new message request from Maria Gomez. Read: https://messages.example.com/requests/4421", ""),
    # Appointment/booking confirmations
    ("review_appointment_confirm", "Your dentist appointment is confirmed for June 3 at 10:30am. Reschedule: https://booking.example.com/appt/44221", ""),
    ("review_flight_checkin", "Check-in now open for your flight AV-8821 BOG-MDE, June 1. Check in: https://airline.example.com/checkin/AV-8821", ""),
    ("review_hotel_booking", "Your reservation at Hotel Caribe is confirmed. Check-in: June 5. Modify booking: https://hotels.example.com/booking/44221", ""),
    # Spanish-language review examples
    ("review_reunion_enlace_es", "Hola equipo, aqui el enlace para la reunion de planificacion: https://meet.example.com/sala/q2-planning. Por favor revisar agenda.", ""),
    ("review_confirmacion_envio_es", "Su envio #COL-4421 esta en camino. Entrega estimada: viernes 30 de mayo. Seguimiento: https://envios.example.com/COL-4421", ""),
    ("review_verificacion_cuenta_es", "Alguien intento acceder a su cuenta desde Medellin. Si fue usted, ignore este mensaje. Revisar actividad: https://seguridad.example.com/actividad", ""),
    ("review_factura_disponible_es", "Su factura electronica de mayo 2026 esta disponible. Consultar: https://facturacion.example.com/consulta/MAYO-2026", ""),
    ("review_codigo_acceso_es", "Su codigo de acceso temporal es: 882144. Valido por 15 minutos. Si no lo solicito, ignore este mensaje.", ""),
    ("review_oferta_curso_es", "Curso gratuito: Introduccion a la ciberseguridad. Inscripciones abiertas: https://cursos.example.com/inscripcion/cyber-intro", ""),
    ("review_recordatorio_cita_es", "Recordatorio: cita medica el 3 de junio a las 9:00am. Confirmar asistencia: https://citas.example.com/confirmar/44221", ""),
    ("review_documento_compartido_es", "Carlos Martinez compartio el documento 'Propuesta Comercial Q2'. Acceder: https://docs.example.com/propuesta-q2", ""),
    ("review_pago_procesado_es", "Pago de $200.000 procesado exitosamente. Comprobante: #CP-8821. Ver detalles: https://pagos.example.com/comprobante/8821", ""),
    ("review_oferta_laboral_es", "Nueva oferta laboral que coincide con tu perfil: Desarrollador Senior. Ver detalles: https://empleos.example.com/oferta/44221", ""),
    # More English borderline
    ("review_domain_renewal", "Your domain example.com expires in 30 days. Renew now to avoid interruption: https://domains.example.com/renew/example.com", ""),
    ("review_ssl_expiry", "SSL certificate for your site expires in 7 days. Auto-renew: https://ssl.example.com/renew/cert-44221", ""),
    ("review_storage_limit", "You have used 85% of your cloud storage. Upgrade plan: https://storage.example.com/upgrade", ""),
    ("review_account_review", "As part of our security review, please verify your account information: https://verify.example.com/kyc/44221", ""),
    ("review_beneficiary_update", "Your bank requires you to confirm beneficiary information. Complete: https://bank.example.com/beneficiary/confirm", ""),
    ("review_subscription_renewal", "Your CyberLureAI Pro subscription renews on June 15. Manage: https://billing.example.com/subscription", ""),
    ("review_data_export", "Your data export is ready for download. File size: 2.3 GB. Download: https://data.example.com/export/batch-44221", ""),
    ("review_api_key_rotate", "Your API key has not been rotated in 90 days. Rotate: https://console.example.com/api-keys/rotate", ""),
    ("review_backup_complete", "Your automated backup completed successfully. Restore point: May 28, 23:00 UTC. Manage: https://backup.example.com/restore", ""),
    ("review_mfa_setup", "Enhance your account security: Set up multi-factor authentication. Start: https://security.example.com/mfa/setup", ""),
    ("review_team_invite", "You have been invited to join 'Engineering Team' workspace. Accept: https://workspace.example.com/join?invite=44221", ""),
    # Calendar/scheduling
    ("review_calendar_shared", "Calendar 'Team PTO' has been shared with you. View: https://calendar.example.com/shared/team-pto", ""),
    ("review_meeting_reschedule", "Meeting 'Sprint Review' has been rescheduled to June 2, 2pm. Accept new time: https://calendar.example.com/event/44221", ""),
    ("review_poll_vote", "Please vote on the team lunch location: https://polls.example.com/vote/lunch-june-2026", ""),
    # Legitimate service notifications
    ("review_service_notice", "We are updating our Terms of Service effective June 15. Review changes: https://legal.example.com/tos/2026-06", ""),
    ("review_maintenance_window", "Scheduled maintenance: June 2, 2am-4am UTC. Service may be briefly unavailable. Details: https://status.example.com/maintenance", ""),
    ("review_feature_announcement", "New feature: Dark mode is now available! Enable in settings: https://app.example.com/settings/appearance", ""),
    ("review_feedback_request", "How was your recent support experience? Rate us: https://feedback.example.com/rate/ticket-44221", ""),
]


def append_to_csv(filepath: Path, examples: list[tuple[str, str, str]]) -> int:
    existing_ids: set[str] = set()
    with filepath.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_ids.add(row["sample_id"])

    new_count = 0
    with filepath.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for sample_id, input_val, signal in examples:
            if sample_id in existing_ids:
                continue
            writer.writerow([sample_id, input_val, "review", signal])
            new_count += 1

    return new_count


def main() -> None:
    url_added = append_to_csv(URL_FILE, URL_REVIEW_EXAMPLES)
    msg_added = append_to_csv(MSG_FILE, MSG_REVIEW_EXAMPLES)
    print(f"URL review examples added: {url_added}")
    print(f"Message review examples added: {msg_added}")
    print(f"Total new review examples: {url_added + msg_added}")


if __name__ == "__main__":
    main()
