import csv
from pathlib import Path

data_dir = Path("D:/PROJECTS/CyberLureAI/data/examples")

new_urls = [
    ["untrusted_cert_on_https_phish", "https://secure-bankverif.com/account/verify", "suspicious", "brand_impersonation,phishing_keywords", "HTTPS phishing domain with keywords but no insecure_http signal. Heuristic may undersignal this because HTTPS suppresses the insecure_http flag."],
    ["idn_homoglyph_apple", "https://www.xn--pple-43da.com/account", "suspicious", "brand_lookalike_domain,phishing_keywords", "IDN homoglyph attack: xn--pple-43da decodes to appe with accent. Current lookalike fails for Unicode chars. Punycode version may still trigger but depends on domain matching."],
    ["keyword_hyphen_obfuscation", "https://example.com/log-in-ver-ify-ac-count", "suspicious", "phishing_keywords,multiple_phishing_keywords", "Keywords broken with hyphens in path (log-in, ver-ify, ac-count). Substrings may still trigger keyword detection but weakened."],
    ["form_hosting_phishing", "https://docs.google.com/forms/d/e/1FAIpQLS/phish", "suspicious", "phishing_keywords", "Legitimate platform Google Forms hosting phishing. No domain signal fires. Only path hints at risk."],
    ["zero_keyword_shortener_phish", "http://bit.ly/2xKpQ9f", "suspicious", "link_shortener,insecure_http", "Shortener + HTTP no phishing keywords in URL. Should be flagged but depends solely on shortener+HTTP combo for scoring."],
    ["data_uri_phish", "http://1.2.3.4/verify?account=locked", "suspicious", "ip_address_destination,phishing_keywords", "IP address + phishing keywords. Classic phish pattern."],
    ["legitimate_domain_redirect", "https://redirect.example.com/?url=https://evil-site.com", "review", "", "Open redirect on legitimate domain. No signal fires. Path has redirect/evil but none in SUSPICIOUS_KEYWORDS."],
    ["suspicious_tld_phish", "https://secure-account.xyz/verify", "suspicious", "phishing_keywords", "Unusual TLD .xyz with phishing keyword. No brand impersonation. Heuristic may undervalue this."],
    ["unusual_port_phish", "http://secure-login.example.com:8080/verify", "suspicious", "insecure_http,phishing_keywords,http_with_phishing_terms", "Non-standard port 8080 + HTTP + phishing keywords. Used to evade blocklists."],
    ["double_extension_trick", "https://invoice-update.pdf.example.com/login", "suspicious", "phishing_keywords,many_subdomains", "Double-extension trick: .pdf in subdomain to look like attachment. 4 labels triggers many_subdomains."],
    ["normal_lookalike_shortener", "http://bit.ly/account-secure-verify", "suspicious", "link_shortener,insecure_http,http_with_phishing_terms", "Shortener + HTTP + 2+ phishing terms. Should trigger multiple high-risk signals."],
    ["path_only_keywords_no_host", "https://safe-domain.example/secure-login-verify-account-update", "suspicious", "phishing_keywords,multiple_phishing_keywords", "Safe-looking domain with heavily keyword-loaded path. Only phishing_keywords + multiple fires. No domain-level signals."],
    ["numbers_in_domain_bank", "https://bank-secure4731.com/login", "suspicious", "phishing_keywords", "Numbers in domain near 'bank' keyword. Not caught by brand lookalike since 'bank' is a keyword not a brand. May be undervalued."],
    ["subdomain_brand_mimic_microsoft", "https://microsoft.support-id3721.example.com/login", "suspicious", "brand_impersonation,phishing_keywords,many_subdomains", "Microsoft impersonation with random suffix in subdomain. Should trigger brand_impersonation."],
    ["fake_paypal_path_query", "https://example.com/paypal/login?secure=verify&account=confirm", "suspicious", "phishing_keywords,multiple_phishing_keywords", "PayPal mentioned in path/query on non-PayPal domain. 'paypal' is a brand but NOT in hostname, so brand_impersonation won't fire. Only keyword detection catches this."],
    ["punycode_mixed_script", "https://www.xn--80ak6aa92e.com/verify", "suspicious", "phishing_keywords", "Punycode domain with Cyrillic script (looks like 'apple.com' in Cyrillic). Heuristic won't catch the homoglyph without Unicode normalization."],
    ["zero_signal_shady_domain", "https://cyberlureai-hack.example.org/login", "review", "phishing_keywords", "Domain hints at malicious intent but no explicit phishing signals beyond login keyword. Only one keyword. Score might be too low."],
    ["excessive_query_params", "https://example.com/login?user=admin&pass=test&redirect=https://evil.com&token=abc123&session=xyz", "suspicious", "phishing_keywords", "Excessive query parameters with suspicious values. Only 'login' as keyword. Heuristic ignores query parameter content."],
    ["base64_encoded_phish", "https://example.com/redirect?d=aHR0cHM6Ly9ldmlsLXNpdGUuY29t", "review", "", "Base64-encoded redirect target in URL parameter. No phishing keywords. Heuristic has zero visibility into encoded content."],
    ["fake_ftp_phish", "ftp://secure-login.example.com/verify", "suspicious", "phishing_keywords", "FTP protocol used for phishing. Not HTTP, so insecure_http won't trigger. Only keyword detection fires. FTP should be treated as higher risk."],
]

new_messages = [
    ["friendly_it_support", "Hey! This is the IT team. We are doing an upgrade and need you to confirm your account. Just click the link: https://portal-it.example.com/confirm", "suspicious", "contains_link", "Friendly-tone phishing without classic urgency keywords. Uses social trust instead of fear. Heuristic likely misses the scam_phrase signal."],
    ["cell_carrier_spoof", "Your wireless bill is ready. View and pay online: https://payment-portal.example.com", "suspicious", "contains_link", "Legitimate-looking carrier notification. No scam phrases, urgency, or threats. Only a link. Heuristic likely misses this entirely."],
    ["hijacked_thread_bec", "Following up on our call earlier. Please approve this wire for $2,500. Link: https://banking-portal.example.com/approve", "suspicious", "contains_link", "Business email compromise style. No scam keywords. Mimics normal business communication. Heuristic misses."],
    ["voice_lure_vishing", "Your bank account has been flagged. Please call 800-555-0199 immediately to verify your identity. Reference code: 48291", "suspicious", "scam_phrase,sensitive_information_request,code_like_number", "Voice phishing lure with phone number. No link. 'bank'+'verify'+'code' triggers. Score check needed."],
    ["delivery_tracking_normal", "Your package from Amazon is out for delivery today. Track it at: https://bit.ly/track-package", "suspicious", "shortened_link", "Normal-looking delivery notification with shortened link. Contains 'today' not in urgency list. 'Amazon' not in scam terms. Shortened link only trigger."],
    ["tax_document_w2_phish", "Your 2025 tax document W-2 is now available. Access your secure portal: https://taxdocs.example.com/login", "suspicious", "contains_link", "W-2 tax phishing. No scam_phrase triggers (no keywords). Only contains_link fires. Heuristic severely undersignals."],
    ["charity_donation_lure", "Donate today to help children in need. Your contribution of $10 makes a difference: https://charity-giving.example.com", "review", "contains_link", "Fake charity donation. No reward/urgency/scam keywords. Emotional manipulation only. Link is sole trigger."],
    ["meeting_invite_spearphish", "Your meeting with the board has been scheduled for tomorrow at 10 AM. Please confirm your attendance: https://meeting-confirm.example.com", "suspicious", "contains_link", "Spear-phishing as meeting invite. 'confirm' not in scam terms. No urgency or threat. Only link trigger."],
    ["job_offer_scam", "Congratulations! You have been selected for the position. Submit your personal details to begin onboarding: https://hr-portal.example.com/onboard", "suspicious", "contains_link", "Fake job offer scam. 'Congratulations' not in REWARD_TERMS. No urgency or threat. Link only trigger."],
    ["fake_reset_password", "Your password expires in 24 hours. To keep using your account, visit: http://password-reset.example.com", "suspicious", "scam_phrase,sensitive_information_request,account_restriction_threat,contains_link", "Password reset phishing. 'password'+'account'+'expires' triggers multiple signals. Check score level."],
    ["no_link_sms_phish", "Bank Alert: Unusual activity detected. Reply YES to confirm or call 800-555-1000 to speak with fraud department.", "suspicious", "scam_phrase", "SMS-style bank phish without URL. 'bank'+'alert' triggers scam_phrase. No link, no code. Heuristic may undersignal."],
    ["invoice_attachment_lure", "Attached is your invoice #48291 for $350. Please review and process payment. Open the attachment for details.", "review", "", "Invoice scam with attachment lure. No link, no scam keywords. 'invoice' not in any keyword list. Heuristic will mark as safe - a blind spot."],
    ["tech_support_popup", "WARNING: Your computer is infected with 5 viruses. Call Microsoft Support at 800-555-0199 immediately. Do not close this message.", "suspicious", "scam_phrase", "Tech support scam popup. 'microsoft'+'warning' triggers scam_phrase. No link. '5' might trigger code-like number."],
    ["romance_scam_opening", "Hi, I saw your profile and I think you are really beautiful. I am an engineer working overseas. Can we chat on WhatsApp? My number is +1-555-0199.", "review", "", "Romance scam opener. No phishing keywords, no links, no urgency. Completely invisible to heuristic. Social engineering blind spot."],
    ["credential_harvesting_doc", "Please review the updated employee handbook and sign the acknowledgment form: https://hr-docs.example.com/handbook-2025", "suspicious", "contains_link", "Credential harvesting via fake document. 'sign'+'acknowledgment' not in keyword lists. Only link trigger fires."],
    ["crypto_investment_scam", "LIMITED OFFER: Invest in Bitcoin today and get 200% returns guaranteed. Click here: https://crypto-profit.example.com", "suspicious", "scam_phrase,contains_link", "Crypto investment scam. 'limited'+'guaranteed' not in current reward/urgency lists. Needs keyword expansion."],
    ["fake_security_alert_sms", "Your Apple ID has been locked for security reasons. Verify now: https://apple-id-verify.example.com", "suspicious", "scam_phrase,contains_link", "SMS Apple ID lockout phish. 'locked'+'Apple'+'verify' triggers scam_phrase. Check signals."],
    ["survey_reward_scam", "Take this 30-second survey and win a free iPhone. Your opinion matters: https://survey-rewards.example.com", "suspicious", "reward_lure,contains_link", "Survey reward scam. 'win'+'free'+'iPhone' triggers reward_lure. Link adds to score."],
    ["polite_urgent_followup", "Gentle reminder: we noticed an issue with your recent payment. Could you please verify your card details when you have a moment? https://billing-help.example.com", "suspicious", "contains_link", "Polite-urgent billing phish. 'payment'+'verify'+'card' - 'card' not in SENSITIVE_TERMS. Tone suppression: politeness may lower perceived threat. Only link trigger likely."],
    ["fake_customer_support", "We are here to help you with your recent order. Your refund of $45.99 is pending. Confirm your bank details here: https://support-refund.example.com", "suspicious", "reward_lure,contains_link", "Fake customer support with refund lure. 'refund' triggers reward_lure. 'confirm'+'bank' may trigger scam_phrase. Check score."],
]

url_path = data_dir / "url_samples.csv"
with open(url_path, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    existing_urls = list(reader)

for row in new_urls:
    existing_urls.append(row)

with open(url_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(existing_urls)

print(f"URL examples: {len(existing_urls)} total (+{len(new_urls)} adversarial)")

msg_path = data_dir / "message_samples.csv"
with open(msg_path, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    existing_msgs = list(reader)

for row in new_messages:
    existing_msgs.append(row)

with open(msg_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(existing_msgs)

print(f"Message examples: {len(existing_msgs)} total (+{len(new_messages)} adversarial)")
