from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'start_datetime', 'end_datetime', 'organiser', 'receiver', 'team')
    list_filter = ('meeting_type', 'start_datetime')
    search_fields = ('title', 'agenda', 'location')
    ordering = ('-start_datetime',)
