from django import forms
from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'start_datetime',
            'end_datetime',
            'meeting_type',
            'location',
            'meeting_link',
            'team',
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
            'meeting_type': forms.Select(attrs={'class': 'sched-input sched-select'}),
            'location': forms.TextInput(attrs={
                'class': 'sched-input',
                'placeholder': 'e.g., Microsoft Teams, Conference Room A',
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'sched-input',
                'placeholder': 'https://...',
            }),
            'team': forms.Select(attrs={'class': 'sched-input sched-select'}),
            'agenda': forms.Textarea(attrs={
                'class': 'sched-input sched-textarea',
                'placeholder': 'Add meeting details, agenda items, or important notes...',
                'rows': 4,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team'].empty_label = '-- Select Team --'
        self.fields['team'].required = False
        self.fields['location'].required = False
        self.fields['meeting_link'].required = False
        self.fields['agenda'].required = False

        # Format datetime values for datetime-local input
        for name in ('start_datetime', 'end_datetime'):
            value = self.initial.get(name) or getattr(self.instance, name, None)
            if value:
                self.initial[name] = value.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')
        if start and end and end <= start:
            self.add_error('end_datetime', 'End time must be after the start time.')
        return cleaned
