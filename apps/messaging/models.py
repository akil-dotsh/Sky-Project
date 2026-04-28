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

    # Who sent it
    sender = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='sent_messages'
    )

    

    # Who receives it (individual)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_messages'
    )

    # OR team recipient
    recipient_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_messages'
    )

    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES
    )

    subject = models.CharField(max_length=255)
    body = models.TextField()

    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Sent'
    )

    is_draft = models.BooleanField(default=False)  # 👈 ADD HERE

    attachment = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True
    )

    def clean(self):
        # Ensure correct recipient logic
        if self.recipient_type == 'Individual':
            if not self.recipient or self.recipient_team:
                raise ValidationError(
                    "Individual messages must have a recipient user only."
                )

        elif self.recipient_type == 'Team':
            if not self.recipient_team or self.recipient:
                raise ValidationError(
                    "Team messages must have a recipient team only."
                )

    def __str__(self):
        if self.recipient_type == 'Individual':
            return f"{self.subject} ({self.sender} → {self.recipient})"
        return f"{self.subject} ({self.sender} → Team)"