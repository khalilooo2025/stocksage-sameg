"""
Common — Modèles de base abstraits.
Tous les modèles métier héritent de ces classes.
"""
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """Modèle abstrait avec timestamps automatiques."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        abstract = True


class UserStampedModel(TimeStampedModel):
    """Modèle abstrait avec traçabilité utilisateur."""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_created',
        verbose_name='Créé par'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_updated',
        verbose_name='Modifié par'
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Modèle abstrait avec suppression douce (archivage)."""
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    archived_at = models.DateTimeField(null=True, blank=True, verbose_name='Archivé le')

    class Meta:
        abstract = True

    def archive(self):
        from django.utils import timezone
        self.is_active = False
        self.archived_at = timezone.now()
        self.save(update_fields=['is_active', 'archived_at'])
