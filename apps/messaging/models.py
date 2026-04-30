from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from apps.teams.models import Team


class Message(models.Model):
    """Unmanaged view of the ERD `Message` table.

    The table is created by the team's hand-written SQL DDL. Django binds
    to it with managed=False so we don't end up with a duplicate
    `messaging_message` table.

    Schema constraints enforced at the DB level (not duplicated here):
      - recipient_type IN ('Individual', 'Team')
      - status         IN ('Queued','Sent','Delivered','Read','Failed')
      - Individual ⇒ recipient_id NOT NULL AND recipient_team_id IS NULL
      - Team       ⇒ recipient_team_id NOT NULL AND recipient_id IS NULL

    Drafts are messages where `sent_at IS NULL` — there's no separate
    is_draft column in the table.
    """

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

    message_id = models.AutoField(primary_key=True, db_column='message_id')

    sender = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='sender_user_id',
        related_name='sent_messages',
    )

    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES,
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column='recipient_id',
        related_name='received_messages',
    )

    recipient_team = models.ForeignKey(
        Team,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column='recipient_team_id',
        related_name='team_messages',
    )

    subject = models.CharField(max_length=255)
    body = models.TextField()

    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Queued',
    )

    attachment = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True,
        db_column='attachment_url',
    )

    class Meta:
        managed = False
        db_table = 'Message'
        ordering = ['-sent_at', '-message_id']

    @property
    def is_draft(self):
        """Drafts are messages that haven't been sent yet."""
        return self.sent_at is None

    def clean(self):
        if self.recipient_type == 'Individual':
            if not self.recipient_id or self.recipient_team_id:
                raise ValidationError(
                    "Individual messages must have a recipient user only."
                )
        elif self.recipient_type == 'Team':
            if not self.recipient_team_id or self.recipient_id:
                raise ValidationError(
                    "Team messages must have a recipient team only."
                )

    def __str__(self):
        if self.recipient_type == 'Individual':
            return f"{self.subject} ({self.sender} -> {self.recipient})"
        return f"{self.subject} ({self.sender} -> {self.recipient_team})"
