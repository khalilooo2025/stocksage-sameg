"""Audit — Journal des actions utilisateurs."""
from django.db import models
from django.conf import settings


class AuditAction(models.TextChoices):
    CREATE = 'CREATE', 'Création'
    UPDATE = 'UPDATE', 'Modification'
    DELETE = 'DELETE', 'Suppression'
    LOGIN = 'LOGIN', 'Connexion'
    LOGOUT = 'LOGOUT', 'Déconnexion'
    VALIDATE = 'VALIDATE', 'Validation'
    VIEW = 'VIEW', 'Consultation'


class AuditLog(models.Model):
    """Entrée de journal d'audit."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        verbose_name='Utilisateur'
    )
    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        verbose_name='Action'
    )
    model_name = models.CharField(max_length=100, blank=True, verbose_name='Modèle')
    object_id = models.CharField(max_length=50, blank=True, verbose_name='ID objet')
    object_repr = models.CharField(max_length=300, blank=True, verbose_name='Représentation')
    changes = models.TextField(null=True, blank=True, verbose_name='Changements')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    user_agent = models.CharField(max_length=300, blank=True, verbose_name='User-Agent')
    url = models.CharField(max_length=500, blank=True, verbose_name='URL')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journal d\'audit'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        user_str = str(self.user) if self.user else 'Anonyme'
        return f'{self.created_at:%Y-%m-%d %H:%M} — {user_str} — {self.action}'
