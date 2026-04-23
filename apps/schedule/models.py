from django.db import models
from django.contrib.auth.models import User
from apps.teams.models import Team


class Meeting(models.Model):
    MEETING_TYPE_CHOICES = [
        ('online', 'Online'),
        ('physical', 'Physical'),
    ]

    meeting_id = models.AutoField(primary_key=True, db_column='meeting_id')

    organiser = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='organiser_user_id',
        related_name='organised_meetings',
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='receiver_user_id',
        related_name='received_meetings',
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='team_id',
        related_name='meetings',
    )

    meeting_type = models.CharField(
        max_length=16,
        choices=MEETING_TYPE_CHOICES,
        default='online',
    )
    title = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    agenda = models.TextField(blank=True, null=True)
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} — {self.start_datetime:%Y-%m-%d %H:%M}"
