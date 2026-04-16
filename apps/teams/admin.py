from django.contrib import admin
from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    # This makes the slug generate automatically as you type the name in Admin!
    prepopulated_fields = {'slug': ('name','department', 'leader', 'dept_head', 'jira_project','focus_areas','tech_stack', )} 
    list_display = ('name', 'department', 'leader', 'dept_head', 'jira_project','focus_areas','tech_stack', )