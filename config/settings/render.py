"""
Settings pour déploiement sur Render.com (free tier).
Hérite de production mais sans Redis (LocMemCache) et utilise DATABASE_URL.
"""
from .production import *
import dj_database_url
import os

# Render fournit DATABASE_URL automatiquement depuis la DB liée
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
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

# Render gère HTTPS en amont (pas besoin de redirect)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email console (pour les tests)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ALLOWED_HOSTS — Render injecte l'URL réelle
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.onrender.com').split(',')
