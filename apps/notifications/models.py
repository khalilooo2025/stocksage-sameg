"""Notifications — Système d'alertes interne."""
from django.db import models
from django.conf import settings


class NotificationType(models.TextChoices):
    INFO = 'info', 'Information'
    SUCCESS = 'success', 'Succès'
    WARNING = 'warning', 'Avertissement'
    DANGER = 'danger', 'Alerte'


class Notification(models.Model):
    """Notification destinée à un utilisateur."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinataire'
    )
    title = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(blank=True, verbose_name='Message')
    notification_type = models.CharField(
        max_length=10,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name='Type'
    )
    link = models.CharField(max_length=200, blank=True, verbose_name='Lien')
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'[{self.get_notification_type_display()}] {self.title} → {self.user}'

    @classmethod
    def send(cls, user, title, message='', notification_type=NotificationType.INFO, link=''):
        """Crée une notification pour un utilisateur."""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )

    @classmethod
    def broadcast(cls, users, title, message='', notification_type=NotificationType.INFO, link=''):
        """Crée une notification pour plusieurs utilisateurs."""
        notifications = [
            cls(
                user=u,
                title=title,
                message=message,
                notification_type=notification_type,
                link=link,
            )
            for u in users
        ]
        cls.objects.bulk_create(notifications)
