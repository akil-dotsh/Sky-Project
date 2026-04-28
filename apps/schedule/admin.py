"""
File:        apps/schedule/admin.py
Author:      Ryan Thompson (W1789088)
Module:      5COSC021W — Software Development Group Project
Description: Django admin registrations for the Meeting and
             MeetingParticipant models so admins can manage records
             via the standard /admin/ panel.
Co-authors:  None.
"""

from django.contrib import admin
from .models import Meeting, MeetingParticipant


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'start_datetime', 'end_datetime', 'organiser', 'receiver', 'team')
    list_filter = ('meeting_type', 'start_datetime')
    search_fields = ('title', 'agenda', 'location')
    ordering = ('-start_datetime',)


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'meeting', 'join_status', 'date', 'joined_at')
    list_filter = ('join_status',)
    search_fields = ('user__username', 'meeting__title')
