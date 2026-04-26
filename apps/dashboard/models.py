from django.db import models
from apps.reports.models import JiraBoard,JiraProject

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.TextField()
    purpose = models.TextField()
    responsibility = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    status = models.TextField(
        default='Draft',
        choices=[
            ('Draft', 'Draft'),
            ('Active', 'Active'),
            ('Deactive', 'Deactive'),
            ('On Hold', 'On Hold'),
            ('Archived', 'Archived'),
        ]
    )

    created_at = models.TextField(blank=True, null=True)
    updated_at = models.TextField(blank=True, null=True)

    team_email = models.TextField()
    on_call_contact = models.TextField()
    location = models.TextField(blank=True, null=True)
    last_reviewed_at = models.TextField(blank=True, null=True)
    development_focus_area = models.TextField(blank=True, null=True)
    key_skills_technology = models.TextField(blank=True, null=True)
    software_owned = models.TextField(blank=True, null=True)

    agile_practice = models.TextField(
        default='Scrum',
        choices=[
            ('Scrum', 'Scrum'),
            ('Kanban', 'Kanban'),
            ('Hybrid', 'Hybrid'),
            ('Others', 'Others'),
            ('None', 'None'),
        ]
    )

    daily_standup_time = models.TextField(blank=True, null=True)
    concurrent_working_range = models.TextField(blank=True, null=True)
    team_wiki_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Team'

    def __str__(self):
        return self.team_name

    jira_project = models.ForeignKey(
        JiraProject,
        on_delete=models.RESTRICT,
        db_column='jira_project_id'
    )
'''
    department = models.ForeignKey(
        Department,
        on_delete=models.RESTRICT,
        db_column='department_id'
    )

'''
