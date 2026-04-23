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


from django.db import models


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('Team Health Summary', 'Team Health Summary'),
        ('Delivery / Velocity', 'Delivery / Velocity'),
        ('Dependency Risk', 'Dependency Risk'),
        ('Governance & Access', 'Governance & Access'),
        ('Messaging & Comms', 'Messaging & Comms'),
        ('Custom', 'Custom'),
    ]

    STATUS_CHOICES = [
        ('Successful', 'Successful'),
        ('Running', 'Running'),
        ('Failed', 'Failed'),
    ]

    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('Excel', 'Excel'),
        ('Dashboard', 'Dashboard'),
    ]

    SCHEDULE_FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    report_id = models.AutoField(primary_key=True)
    report_name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100, choices=REPORT_TYPE_CHOICES)
    report_format = models.CharField(max_length=50, choices=FORMAT_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Running')

    scope = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)

    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    compare_previous = models.BooleanField(default=False)

    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(
        max_length=20,
        choices=SCHEDULE_FREQUENCY_CHOICES,
        blank=True,
        null=True
    )
    next_run_at = models.DateTimeField(blank=True, null=True)
    last_run_at = models.DateTimeField(blank=True, null=True)

    report_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    team_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'Report'

    def __str__(self):
        return self.report_name

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