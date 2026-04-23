from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'end_datetime', 'meeting_type', 'team', 'organiser', 'created_at')
    list_filter = ('meeting_type', 'team', 'start_datetime')
    search_fields = ('title', 'agenda', 'location')
    ordering = ('-start_datetime',)
