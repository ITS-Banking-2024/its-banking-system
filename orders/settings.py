from django.conf import settings

# this lets us configure the product model from the main project file,
# without creating a dependency to the main project file
PRODUCT_MODEL = getattr(settings, 'PRODUCT_MODEL')
CUSTOMER_MODEL = getattr(settings, 'CUSTOMER_MODEL')