"""
Users — Modèle utilisateur avec rôles stricts.
4 rôles : Administrateur, Manager, Magasinier, Technicien
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import TimeStampedModel


class Role(models.TextChoices):
    ADMIN = 'admin', 'Administrateur'
    MANAGER = 'manager', 'Manager'
    MAGASINIER = 'magasinier', 'Magasinier'
    TECHNICIEN = 'technicien', 'Technicien'


class User(AbstractUser):
    """
    Utilisateur personnalisé avec rôle métier.
    Remplace le User Django standard.
    """
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TECHNICIEN,
        verbose_name='Rôle'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Téléphone'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser

    @property
    def is_manager(self):
        return self.role == Role.MANAGER

    @property
    def is_magasinier(self):
        return self.role == Role.MAGASINIER

    @property
    def is_technicien(self):
        return self.role == Role.TECHNICIEN

    @property
    def can_see_prices(self):
        """RÈGLE NON NÉGOCIABLE : le technicien ne voit jamais les prix."""
        return not self.is_technicien

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[-1][0]}'.upper()
        return self.username[:2].upper()
