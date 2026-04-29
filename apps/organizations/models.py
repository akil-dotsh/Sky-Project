from django.db import models
from django.contrib.auth.models import User

# Models that directly access existing sky.db tables

class Department(models.Model):
    department_id = models.AutoField(primary_key=True, db_column='department_id')
    department_name = models.CharField(max_length=255, db_column='department_name', blank=True, null=True)
    dept_head_user_id = models.IntegerField(db_column='dept_head_user_id', blank=True, null=True)
    department_email = models.CharField(max_length=255, db_column='department_email', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Department'

    def __str__(self):
        return self.department_name or f"Department {self.department_id}"


class Team(models.Model):
    team_id = models.AutoField(primary_key=True, db_column='team_id')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id', blank=True, null=True)
    team_name = models.CharField(max_length=255, db_column='team_name', blank=True, null=True)
    development_focus_area = models.CharField(max_length=255, db_column='development_focus_area', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Team'

    def __str__(self):
        return self.team_name or f"Team {self.team_id}"


class Dependency(models.Model):
    dependency_id = models.AutoField(primary_key=True, db_column='dependency_id')
    dependency_name = models.CharField(max_length=255, db_column='dependency_name', blank=True, null=True)
    criticality = models.CharField(max_length=255, db_column='criticality', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Dependency'

    def __str__(self):
        return self.dependency_name or f"Dependency {self.dependency_id}"


class TeamDependency(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_column='team_id')
    dependency = models.ForeignKey(Dependency, on_delete=models.CASCADE, db_column='dependency_id')
    dependency_type = models.CharField(max_length=255, db_column='dependency_type', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TeamDependency'
        unique_together = [['team', 'dependency']]
        # Don't add automatic id field
        default_related_name = 'team_dependencies'

    def __str__(self):
        return f"{self.team} - {self.dependency} ({self.dependency_type})"
