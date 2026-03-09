"""Settings pour développement local."""
from .base import *

DEBUG = True

# SQLite pour le développement local (pas besoin de PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache local (pas besoin de Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# En local on peut utiliser la session auth aussi
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].append(
    'rest_framework.authentication.BasicAuthentication'
)

# Email en console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar (optionnel)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
