from django import forms
from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'time', 'platform', 'team', 'agenda']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'sched-input',
                'placeholder': 'e.g., Sprint Planning Session',
            }),
            'date': forms.DateInput(attrs={
                'class': 'sched-input',
                'type': 'date',
            }),
            'time': forms.TimeInput(attrs={
                'class': 'sched-input',
                'type': 'time',
            }),
            'platform': forms.Select(attrs={'class': 'sched-input sched-select'}),
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
        self.fields['agenda'].required = False
