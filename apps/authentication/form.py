from django import forms
from django.core import validators


class AdminLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'sky@admin.com',
        'maxlength': 100,
        'required': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'PASSWORD',
        'maxlength': 100,
        'minlength': 4,
        'required': True
    }))


    def clean(self):
        cleaned_data = super(AdminLoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

