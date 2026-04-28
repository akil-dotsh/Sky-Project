"""
File:        apps/schedule/forms.py
Author:      Ryan Thompson (W1789088)
Module:      5COSC021W — Software Development Group Project
Description: ModelForm for creating/editing Meeting records. Wires the
             ERD's mutex constraint at the form layer (Individual ⇒
             recipient required, no team; Team ⇒ team required, no
             recipient) so users get inline feedback instead of a
             database CHECK violation.
Co-authors:  None.
"""

from django import forms
from django.contrib.auth.models import User

from .models import Meeting, ScheduleTeam


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'start_datetime',
            'end_datetime',
            'meeting_type',
            'receiver',
            'team',
            'location',
            'meeting_link',
            'agenda',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'sched-input',
                'placeholder': 'e.g., Sprint Planning Session',
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'sched-input',
                'type': 'datetime-local',
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'sched-input',
                'type': 'datetime-local',
            }),
            'meeting_type': forms.Select(attrs={'class': 'sched-input sched-select', 'data-meeting-type': '1'}),
            'receiver': forms.Select(attrs={'class': 'sched-input sched-select'}),
            'team': forms.Select(attrs={'class': 'sched-input sched-select'}),
            'location': forms.TextInput(attrs={
                'class': 'sched-input',
                'placeholder': 'e.g., Conference Room A (optional)',
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'sched-input',
                'placeholder': 'https://...',
            }),
            'agenda': forms.Textarea(attrs={
                'class': 'sched-input sched-textarea',
                'placeholder': 'Agenda items, notes, etc.',
                'rows': 4,
            }),
        }

    def __init__(self, *args, organiser=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._organiser = organiser
        self.fields['team'].queryset = ScheduleTeam.objects.all().order_by('team_name')
        self.fields['team'].empty_label = '-- Select Team --'
        self.fields['team'].required = False
        receiver_qs = User.objects.all().order_by('first_name', 'last_name', 'username')
        if organiser is not None and getattr(organiser, 'pk', None):
            receiver_qs = receiver_qs.exclude(pk=organiser.pk)
        self.fields['receiver'].queryset = receiver_qs
        self.fields['receiver'].empty_label = '-- Select Recipient --'
        self.fields['receiver'].required = False
        self.fields['location'].required = False
        self.fields['meeting_link'].required = False

        for name in ('start_datetime', 'end_datetime'):
            value = self.initial.get(name) or getattr(self.instance, name, None)
            if value:
                self.initial[name] = value.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned = super().clean()
        mtype = cleaned.get('meeting_type')
        receiver = cleaned.get('receiver')
        team = cleaned.get('team')

        if mtype == 'Individual':
            if not receiver:
                self.add_error('receiver', 'Individual meetings require a recipient.')
            if team:
                self.add_error('team', 'Individual meetings cannot also have a team.')
            if self._organiser and receiver and receiver.pk == self._organiser.pk:
                self.add_error('receiver', 'Recipient cannot be the organiser.')
        elif mtype == 'Team':
            if not team:
                self.add_error('team', 'Team meetings require a team.')
            if receiver:
                self.add_error('receiver', 'Team meetings cannot also have a recipient.')

        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')
        if start and end and end <= start:
            self.add_error('end_datetime', 'End time must be after start time.')

        return cleaned
