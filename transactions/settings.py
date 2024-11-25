from django.conf import settings

ACCOUNT_MODEL = getattr(settings, 'ACCOUNT_MODEL')
STOCK_MODEL = getattr(settings, 'STOCK_MODEL')