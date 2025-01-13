from django.conf import settings


ACCOUNT_MODEL = getattr(settings, 'ACCOUNT_MODEL')
STOCK_MODEL = getattr(settings, 'STOCK_MODEL')
STOCK_OWNERSHIP_MODEL = getattr(settings, 'STOCK_OWNERSHIP_MODEL')
CHECKING_ACCOUNT_MODEL = getattr(settings, 'CHECKING_ACCOUNT_MODEL')
CUSTODY_ACCOUNT_MODEL = getattr(settings, 'CUSTODY_ACCOUNT_MODEL')
