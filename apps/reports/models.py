from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    audit_id = models.AutoField(primary_key=True)
    entity_name = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    changed_by_name = models.TextField()
    changed_at = models.TextField(blank=True, null=True)
    change_summary = models.TextField(blank=True, null=True)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='user_id',
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    class Meta:
        managed = False
        db_table = 'auditLog'

    def __str__(self):
        return f"{self.action} - {self.entity_name}"



class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='notifications'
    )

    title = models.TextField()
    message = models.TextField()
    created_at = models.TextField(blank=True, null=True)
    notification_type = models.TextField(blank=True, null=True)
    link_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Notification'

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Queued', 'Queued'),
        ('Sent', 'Sent'),
        ('Delivered', 'Delivered'),
        ('Read', 'Read'),
        ('Failed', 'Failed'),
    ]

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        db_column='notification_id',
        related_name='user_notifications'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='user_notifications'
    )

    date = models.TextField(primary_key=True)
    delivered_at = models.TextField(blank=True, null=True)

    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='Queued'
    )

    read_at = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'USER_NOTIFICATION'
        unique_together = (('notification', 'user', 'date'),)

    def __str__(self):
        return f"{self.user} - {self.notification} ({self.delivery_status})"