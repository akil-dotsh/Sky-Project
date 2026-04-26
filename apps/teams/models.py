from django.db import models
from django.utils.text import slugify
from apps.authentication.models import UserProfile

#Main Team structure
class Team(models.Model):
    name = models.CharField(max_length=255)  
    department = models.CharField(max_length=255)
    leader = models.CharField(max_length=255)  
    dept_head = models.CharField(max_length=255)  
    jira_project = models.CharField(max_length=255, blank=True, null=True)
    focus_areas = models.TextField(blank=True, null=True)
    tech_stack = models.TextField(blank=True, null=True) 
    github_repo = models.URLField(max_length=500, blank=True, null=True)
    jira_board = models.URLField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    #for cleaner routes
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#Jira integration models
class JiraProject(models.Model):
    name = models.CharField(max_length=255)
    project_key = models.CharField(max_length=50, blank=True)
    team = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='jira_projects')

class JiraBoard(models.Model):
    name = models.CharField(max_length=255)
    board_url = models.URLField()
    team = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='jira_boards')

#Communication Channe;s
class ContactChannel(models.Model):
    CHANNEL_TYPES = [('Slack', 'Slack'), ('Email', 'Email'), ('MS Teams', 'MS Teams')]
    channel_type = models.CharField(max_length=50, choices=CHANNEL_TYPES)
    channel_id = models.CharField(max_length=255) 
    team = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='channels')

#Dependency tracking 
class Dependency(models.Model):
    name = models.CharField(max_length=100) 
    dep_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50) 
    description = models.TextField()

#logig linking two UserProfiles to show who depended on whom
class TeamDependency(models.Model):
    team = models.ForeignKey(
        'authentication.UserProfile', 
        on_delete=models.CASCADE, 
        related_name='dependencies',
        null=True, 
        blank=True
    )
    
    dependent_on = models.ForeignKey(
        'authentication.UserProfile', 
        on_delete=models.CASCADE, 
        related_name='required_by',
        null=True, 
        blank=True
    )
    
    DEPENDENCY_TYPE = [
        ('Upstream', 'Upstream'),
        ('Downstream', 'Downstream'),
    ]
    
    dependency_type = models.CharField(
        max_length=20, 
        choices=DEPENDENCY_TYPE,
        default='Upstream'
    )
    
    status = models.CharField(
        max_length=50, 
        default='Active'
    )

    #string representation for the admin panel
    def __str__(self):
        team_name = self.team.team_id if self.team else "Unknown"
        dep_name = self.dependent_on.team_id if self.dependent_on else "Unknown"
        return f"{team_name} -> {dep_name} ({self.dependency_type})"
    
#Code Repository reference
class CodeRepository(models.Model):
    repo_url = models.URLField()
    branch_name = models.CharField(max_length=100, default='main')
    team = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='repositories')