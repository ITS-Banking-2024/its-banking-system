"""
Django settings for swd_django_demo project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=gtp5z3(w^-$8gm7a4h#tj-=5$lr09#lv522%=wk0)h=dfh^8-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core.apps.CoreConfig',
    'customers.apps.CustomersConfig',
    'products.apps.ProductsConfig',
    'accounts.apps.AccountsConfig',
#    'product_alternative.apps.ProductAlternativeConfig',
    'orders.apps.OrdersConfig',
    'transactions.apps.TransactionsConfig',
    'stock_trading.apps.StockTradingConfig',
]

# Middleware classes used in request-response processing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL routing configuration
ROOT_URLCONF = 'swd_django_demo.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
            'libraries': {
                # 'products_tags': 'products.templatetags.products_tag',
                # we are adding functionality to the products app from the orders app without
                # having the product app depend on the orders app
                'products_tags': 'orders.templatetags.orders_tag',
            }
        },
    },
]

# Static file finders
STATICFILES_FINDERS = ['django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',]

# WSGI application configuration
WSGI_APPLICATION = 'swd_django_demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        # Add other formatters as needed
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'console-verbose': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # Add other handlers as needed for your project
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # Configure custom logger for the app
        'orders': {
            'handlers': ['console-verbose'],
            'level': 'DEBUG',
        },
        # Add other app loggers as needed
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
# for easier testing we will allow unsecure passwords
"""
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 3,
        }
    },
{
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
"""

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'

# Set the directory where collectstatic will put static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add additional directories to look for static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# change default user model to our own
AUTH_USER_MODEL = 'customers.Customer'

# Set the model to use for products
PRODUCT_MODEL = "products.ProductBase"

# Set the model to use for customers
CUSTOMER_MODEL = "customers.CustomerBase"

ACCOUNT_MODEL = "accounts.AccountBase"

TRANSACTION_MODEL = "transactions.TransactionBase"


