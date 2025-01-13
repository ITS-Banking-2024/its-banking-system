from django.conf import settings

ACCOUNT_MODEL = getattr(settings, 'ACCOUNT_MODEL')
CUSTODY_ACCOUNT_MODEL = getattr(settings, 'CUSTODY_ACCOUNT_MODEL')