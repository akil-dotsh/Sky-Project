from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        primary_key=True
    )

    dob = models.DateField(db_column='dob', blank=True, null=True)
    phone= models.CharField(max_length=20, db_column='phone_number', blank=True, null=True)
    address = models.CharField( db_column='address', blank=True,null=True)
    profile_picture = models.TextField(db_column='profile_picture_url',blank=True,null=True)
    bio = models.TextField(db_column='bio', blank=True,null=True)
    office_location = models.TextField(db_column='office_location',blank=True,null=True)
    availability_status = models.TextField(db_column='availability_status',blank=True,null=True)
    team_id = models.TextField(db_column='team_id',blank=True,null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    primary_skills = models.TextField(db_column='primary_skill',blank=True,null=True)
    grade_level = models.TextField(
        db_column='grade_level',
        choices=[
            ('Junior', 'Junior'),
            ('Mid', 'Mid'),
            ('Senior', 'Senior'),
        ],
        default='Junior',
        blank=True,
        null=True)
    github_username = models.TextField(db_column='github_username', blank=True, null=True)
    leader_user_id = models.IntegerField(db_column='leader_user_id', blank=True, null=True)
    leader_since = models.DateField(db_column='leader_since', blank=True, null=True)

    class Meta:
        db_table = 'UserProfile'
        managed = True

    def __str__(self):
        return self.user.username