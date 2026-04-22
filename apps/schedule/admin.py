from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'platform', 'team', 'created_by', 'created_at')
    list_filter = ('platform', 'date', 'team')
    search_fields = ('title', 'agenda')
    ordering = ('-date', '-time')
