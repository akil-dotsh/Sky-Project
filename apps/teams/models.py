from django.db import models
from django.utils.text import slugify

class Team(models.Model):
    name = models.CharField(max_length=255)  # Team Name
    department = models.CharField(max_length=255)
    leader = models.CharField(max_length=255)  # Team Leader
    dept_head = models.CharField(max_length=255)  # Department Head
    jira_project = models.CharField(max_length=255, blank=True, null=True)
    focus_areas = models.TextField(blank=True, null=True)
    tech_stack = models.TextField(blank=True, null=True) # Key Skills & Tech
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name