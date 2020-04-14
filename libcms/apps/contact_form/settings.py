from django.conf import settings

CONTACT_FORM = getattr(settings, 'CONTACT_FORM', {})

MAX_REQUESTS_FROM_IP_PER_MINUTE = CONTACT_FORM.get('max_requests_from_ip_per_minute', 3)
MAX_REQUESTS_PER_MINUTE = CONTACT_FORM.get('max_requests_per_minute', 9)

RECAPTCHA_SECRET = getattr(settings, 'RECAPTCHA_SECRET', '')