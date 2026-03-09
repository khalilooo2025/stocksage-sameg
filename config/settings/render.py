"""
Settings pour déploiement sur Render.com (free tier).
Utilise SQLite si DATABASE_URL absent, sinon PostgreSQL.
"""
from .base import *
import os

DEBUG = False

# Render fournit DATABASE_URL depuis la DB liée (sinon SQLite pour test)
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # SQLite pour test rapide sans base PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Pas de Redis sur le free tier — LocMemCache suffit pour les tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Celery en mode synchrone (pas de broker Redis)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Render gère HTTPS en amont
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email console (pour les tests)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.onrender.com,localhost').split(',')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []  # On laisse vide — static/ créé par build.sh

# SECRET_KEY depuis env
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-render-default-key-change-me')
