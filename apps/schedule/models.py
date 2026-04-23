from django.db import models
from django.contrib.auth.models import User


class ScheduleTeam(models.Model):
    """Read-only view of the ERD `Team` table used for the schedule team dropdown.

    The team data lives in the hand-written `Team` table (see CW1 logical design),
    not Django's `teams_team`. Declaring this model as unmanaged lets us reference
    it via a FK without Django trying to create or migrate the table.
    """

    team_id = models.AutoField(primary_key=True, db_column='team_id')
    team_name = models.CharField(max_length=255, db_column='team_name')

    class Meta:
        managed = False
        db_table = 'Team'

    def __str__(self):
        return self.team_name


class Meeting(models.Model):
    """Django ORM view of the ERD `Meeting` table.

    The `Meeting` table is defined by the team's SQL schema (CW1 design) and
    enforces:
      - meeting_type ∈ {'Individual', 'Team'}
      - Individual ⇒ receiver_user_id NOT NULL AND team_id IS NULL
      - Team       ⇒ team_id         NOT NULL AND receiver_user_id IS NULL
      - end_datetime > start_datetime
      - organiser_user_id ≠ receiver_user_id (for Individual)
    """

    MEETING_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team'),
    ]

    meeting_id = models.AutoField(primary_key=True, db_column='meeting_id')

    organiser = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='organiser_user_id',
        related_name='organised_meetings',
    )
    meeting_type = models.CharField(
        max_length=16,
        choices=MEETING_TYPE_CHOICES,
        default='Team',
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='receiver_user_id',
        null=True,
        blank=True,
        related_name='received_meetings',
    )
    team = models.ForeignKey(
        ScheduleTeam,
        on_delete=models.DO_NOTHING,
        db_column='team_id',
        null=True,
        blank=True,
        related_name='meetings',
    )

    title = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    agenda = models.TextField()
    meeting_link = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Meeting'
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} ({self.start_datetime:%Y-%m-%d %H:%M})"


class MeetingParticipant(models.Model):
    """Unmanaged view of the ERD `Meeting_Participant` junction table.

    Composite PK is (user_id, meeting_id, date). We declare `user` as the
    Django primary key so the ORM has a single attribute to hang queries
    off; uniqueness is already enforced at the table level.
    """

    JOIN_STATUS_CHOICES = [
        ('Invited', 'Invited'),
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined'),
        ('Joined', 'Joined'),
        ('No Show', 'No Show'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='user_id',
        primary_key=True,
        related_name='meeting_participations',
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.DO_NOTHING,
        db_column='meeting_id',
        related_name='participants',
    )
    date = models.DateTimeField(db_column='date')
    join_status = models.CharField(
        max_length=16,
        choices=JOIN_STATUS_CHOICES,
        default='Invited',
    )
    joined_at = models.DateTimeField(db_column='joined_at', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Meeting_Participant'
        unique_together = (('user', 'meeting', 'date'),)

    def __str__(self):
        return f"{self.user} in {self.meeting} ({self.join_status})"
