from django import forms
from django.contrib.auth.models import User
from django.core import validators

class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'John',
            'id': 'first_name',
            'required': True
    })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Doe',
            'id': 'last_name',
            'required': True
        })
    )
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your.email@sky.com',
            'id': 'email',
            'required': True
        })
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-lg',
            'id':'dob',
            'type': 'date',
            'required': True
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'id':'phone',
            'placeholder': '074........',
            'required': True
        })
    )
    password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id':'password',
            'placeholder': 'Password',
            'required': True
        })
    )
    confirm_password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id':'confirm_password',
            'placeholder': 'Confirm Password',
            'required': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data



class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'user@sky.com',
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
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')


class ForgotPasswordForm(forms.Form):
    #form to capture the user's email address
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'user@sky.com',
        'maxlength': 100,
        'required': True
    }))

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()
        email = cleaned_data.get('email')