from django.db import models
from django.contrib.auth.models import User
from apps.teams.models import Team


class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('Microsoft Teams', 'Microsoft Teams'),
        ('Zoom', 'Zoom'),
        ('Google Meet', 'Google Meet'),
        ('In Person', 'In Person'),
        ('Slack Huddle', 'Slack Huddle'),
    ]

    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    platform = models.CharField(max_length=64, choices=PLATFORM_CHOICES, default='Microsoft Teams')
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings',
    )
    agenda = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_meetings',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"
