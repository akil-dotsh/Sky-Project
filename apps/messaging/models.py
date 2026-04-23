from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from apps.teams.models import Team


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    RECIPIENT_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team'),
    ]

    STATUS_CHOICES = [
        ('Queued', 'Queued'),
        ('Sent', 'Sent'),
        ('Delivered', 'Delivered'),
        ('Read', 'Read'),
        ('Failed', 'Failed'),
    ]

    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='recipient_id',
        null=True,
        blank=True,
        related_name='received_messages'
    )

    recipient_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        db_column='recipient_team_id',
        null=True,
        blank=True,
        related_name='team_messages'
    )

    subject = models.TextField()
    body = models.TextField()

    sent_at = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Queued'
    )

    attachment_url = models.TextField(blank=True, null=True)
    read_at = models.TextField(blank=True, null=True)

    sender_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='sender_user_id',
        related_name='sent_messages'
    )

    class Meta:
        managed = False
        db_table = 'Message'

    def clean(self):
        if self.recipient_type == 'Individual':
            if not self.recipient or self.recipient_team:
                raise ValidationError(
                    "For Individual messages, recipient must be set "
                )

        elif self.recipient_type == 'Team':
            if not self.recipient_team or self.recipient:
                raise ValidationError(
                    "For Team messages, recipient_team must be set "
                )

    def __str__(self):
        return f"{self.subject} ({self.recipient_type})"