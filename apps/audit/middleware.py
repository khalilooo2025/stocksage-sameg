"""Middleware d'audit — enregistre les connexions et déconnexions."""
from django.utils.deprecation import MiddlewareMixin
from apps.common.utils import get_client_ip


class AuditMiddleware(MiddlewareMixin):
    """Middleware qui enregistre les actions importantes dans le journal d'audit."""

    def process_response(self, request, response):
        # On n'audite pas les requêtes statiques/media ou API
        path = request.path
        if any(path.startswith(p) for p in ['/static/', '/media/', '/api/']):
            return response

        # Enregistrer login/logout via signals (voir signals.py)
        # Ce middleware peut être étendu pour auditer d'autres actions
        return response
