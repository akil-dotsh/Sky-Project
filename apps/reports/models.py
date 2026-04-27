from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """
    Maps the existing auditLog table.
    Used to record important dashboard/system actions.
    """

    audit_id = models.AutoField(
        primary_key=True,
        db_column="audit_id"
    )

    entity_name = models.TextField(
        db_column="entity_name",
        blank=True,
        null=True
    )

    action = models.TextField(
        db_column="action",
        blank=True,
        null=True
    )

    changed_by_name = models.TextField(
        db_column="changed_by_name",
        blank=True,
        null=True
    )

    changed_at = models.TextField(
        db_column="changed_at",
        blank=True,
        null=True
    )

    change_summary = models.TextField(
        db_column="change_summary",
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column="user_id",
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    class Meta:
        managed = False
        db_table = "auditLog"

    def __str__(self):
        return f"{self.entity_name} - {self.action}"


class Notification(models.Model):
    """
    Maps the existing Notification table.

    user_id in this table means the user who created/generated the notification.
    """

    notification_id = models.AutoField(
        primary_key=True,
        db_column="notification_id"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="created_notifications"
    )

    title = models.TextField(
        db_column="title"
    )

    message = models.TextField(
        db_column="message"
    )

    created_at = models.TextField(
        db_column="created_at",
        blank=True,
        null=True
    )

    notification_type = models.TextField(
        db_column="notification_type",
        blank=True,
        null=True
    )

    link_url = models.TextField(
        db_column="link_url",
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "Notification"

    def __str__(self):
        return self.title


class Report(models.Model):
    """
    Main Report table created and managed by Django.
    """

    REPORT_TYPE_CHOICES = [
        ("Team Health Summary", "Team Health Summary"),
        ("Delivery / Velocity", "Delivery / Velocity"),
        ("Dependency Risk", "Dependency Risk"),
        ("Governance & Access", "Governance & Access"),
        ("Messaging & Comms", "Messaging & Comms"),
        ("Custom", "Custom"),
    ]

    STATUS_CHOICES = [
        ("Successful", "Successful"),
        ("Running", "Running"),
        ("Failed", "Failed"),
    ]

    FORMAT_CHOICES = [
        ("PDF", "PDF"),
        ("Excel", "Excel"),
        ("Dashboard", "Dashboard"),
    ]

    SCHEDULE_FREQUENCY_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
    ]

    report_id = models.AutoField(
        primary_key=True
    )

    report_name = models.CharField(
        max_length=255
    )

    report_type = models.CharField(
        max_length=100,
        choices=REPORT_TYPE_CHOICES
    )

    report_format = models.CharField(
        max_length=50,
        choices=FORMAT_CHOICES
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Running"
    )

    scope = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    department = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    from_date = models.DateField(
        blank=True,
        null=True
    )

    to_date = models.DateField(
        blank=True,
        null=True
    )

    compare_previous = models.BooleanField(
        default=False
    )

    is_scheduled = models.BooleanField(
        default=False
    )

    schedule_frequency = models.CharField(
        max_length=20,
        choices=SCHEDULE_FREQUENCY_CHOICES,
        blank=True,
        null=True
    )

    next_run_at = models.DateTimeField(
        blank=True,
        null=True
    )

    last_run_at = models.DateTimeField(
        blank=True,
        null=True
    )

    report_url = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    team_id = models.IntegerField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "Report"

    def __str__(self):
        return self.report_name


class UserNotification(models.Model):
    """
    Maps the existing USER_NOTIFICATION table.

    user_id in this table means the user who received/read the notification.

    Important:
    Your database table does not have an id column.
    Your DB uses notification_id + user_id + date as a composite primary key.
    Django does not fully support composite primary keys, so date is used as
    the Django primary key workaround.
    """

    DELIVERY_STATUS_CHOICES = [
        ("Queued", "Queued"),
        ("Sent", "Sent"),
        ("Delivered", "Delivered"),
        ("Read", "Read"),
        ("Failed", "Failed"),
    ]

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        db_column="notification_id",
        related_name="user_notifications"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="received_notifications"
    )

    date = models.TextField(
        primary_key=True,
        db_column="date"
    )

    delivered_at = models.TextField(
        db_column="delivered_at",
        blank=True,
        null=True
    )

    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        db_column="delivery_status",
        default="Queued"
    )

    read_at = models.TextField(
        db_column="read_at",
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "USER_NOTIFICATION"
        unique_together = (("notification", "user", "date"),)

    def __str__(self):
        return f"{self.user.username} - {self.notification.title} ({self.delivery_status})"


class JiraBoard(models.Model):
    """
    Maps the existing JiraBoard table.
    """

    jiraBoard_id = models.AutoField(
        primary_key=True,
        db_column="jiraBoard_id"
    )

    board_name = models.TextField(
        db_column="board_name"
    )

    board_type = models.TextField(
        db_column="board_type",
        default="Scrum",
        choices=[
            ("Scrum", "Scrum"),
            ("Kanban", "Kanban"),
            ("Backlog", "Backlog"),
            ("Bug Tracking", "Bug Tracking"),
        ]
    )

    is_active = models.BooleanField(
        db_column="is_active",
        default=True
    )

    created_at = models.TextField(
        db_column="created_at",
        blank=True,
        null=True
    )

    updated_at = models.TextField(
        db_column="updated_at",
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "JiraBoard"

    def __str__(self):
        return self.board_name


class JiraProject(models.Model):
    """
    Maps the existing JiraProject table.
    """

    jira_project_id = models.AutoField(
        primary_key=True,
        db_column="jira_project_id"
    )

    project_name = models.TextField(
        db_column="project_name"
    )

    description = models.TextField(
        db_column="description",
        blank=True,
        null=True
    )

    project_type = models.TextField(
        db_column="project_type",
        default="Software",
        choices=[
            ("Software", "Software"),
            ("Service", "Service"),
            ("Infrastructure", "Infrastructure"),
            ("Research", "Research"),
            ("Maintenance", "Maintenance"),
            ("Support", "Support"),
        ]
    )

    created_at = models.TextField(
        db_column="created_at",
        blank=True,
        null=True
    )

    status = models.TextField(
        db_column="status",
        default="Active",
        choices=[
            ("Active", "Active"),
            ("On Hold", "On Hold"),
            ("Completed", "Completed"),
            ("Archived", "Archived"),
        ]
    )

    jiraBoard = models.ForeignKey(
        JiraBoard,
        on_delete=models.DO_NOTHING,
        db_column="jiraBoard_id"
    )

    class Meta:
        managed = False
        db_table = "JiraProject"

    def __str__(self):
        return self.project_name


class ResourceLink(models.Model):
    """
    Maps the existing ResourceLink table.
    """

    resource_id = models.AutoField(
        primary_key=True,
        db_column="resource_id"
    )

    resource_type = models.TextField(
        db_column="resource_type",
        default="report"
    )

    documentation = models.TextField(
        db_column="documentation",
        blank=True,
        null=True
    )

    description = models.TextField(
        db_column="description",
        blank=True,
        null=True
    )

    resource_value = models.TextField(
        db_column="resource_value",
        blank=True,
        null=True
    )

    report_url = models.TextField(
        db_column="report_url",
        blank=True,
        null=True
    )

    created_at = models.TextField(
        db_column="created_at",
        blank=True,
        null=True
    )

    team_id = models.IntegerField(
        db_column="team_id"
    )

    class Meta:
        managed = False
        db_table = "ResourceLink"

    def __str__(self):
        return f"{self.resource_type} - Team {self.team_id}"