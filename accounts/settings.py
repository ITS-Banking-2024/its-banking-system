from django.conf import settings

CUSTOMER_MODEL = getattr(settings, 'CUSTOMER_MODEL')
CONCRETE_CUSTOMER_MODEL = getattr(settings, 'CONCRETE_CUSTOMER_MODEL')