# Author: Akil Hossain
# Student ID: 20270054

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from apps.authentication.form import LoginForm, RegistrationForm, ForgotPasswordForm
from apps.authentication.models import UserProfile

#Backend logic how each user should be authenticated before login/registration/password-reset
def user_register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            dob = form.cleaned_data['dob']
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            # Using email as username
            username = email

            try:
                with transaction.atomic():
                    # Save main auth user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )

                    # Extra info inside UserProfile table
                    UserProfile.objects.create(
                        user=user,
                        dob=dob,
                        phone=phone
                    )

                login(request, user)
                return redirect('dev_login')

            except Exception as e:
                return render(request, 'authentication/register.html', {
                    'form': form,
                    'error': 'Registration failed. Please try again.'
                })

    return render(request, 'authentication/register.html', {
        'form': form,
    })


def user_login(request,template_name):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                user_obj=None

            if user_obj:
                user = authenticate(request,username=username, password=password)

                if user is not None:
                    #Only admin and Deprtment head
                    if user.is_superuser or user.groups.filter(name='Department Head').exists():
                        login(request,user)
                        return redirect('management_dashboard')
                    # Only Team leader and Developer
                    elif user.groups.filter(name='Team Leader').exists() or user.groups.filter(name='Developer').exists():
                        login(request,user)
                        return redirect('staff_dashboard')
                    else:
                        return render(request,template_name,{
                          'form':form,
                          'error':'Access denied. Contact your manager.'
                        })

                else:
                    return render(request,template_name,{
                        'form':form,
                        'error':'Invalid Credentials'
                    })

            else:
                return render(request,template_name,{
                    'form':form,
                    'error':'Invalid Credentials'
                })

    return render(request,template_name,{
            'form':form,
        })

def admin_login(request):
    return user_login(request,'authentication/admin_dept_login.html')

def dev_login(request):
    return user_login(request,'authentication/dev_leader_login.html')


def forgot_password(request):
    form = ForgotPasswordForm()

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user_obj = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user_obj = None

            if user_obj:
                if not user_obj.is_active:
                    return render(request, 'authentication/forgot_password.html', {
                        'form': form,
                        'error': 'Your account is inactive. Please contact your manager to activate your account.'
                    })

                current_site = get_current_site(request)

                subject = render_to_string(
                    'authentication/password_reset_subject.txt'
                ).strip()

                message = render_to_string(
                    'authentication/password_reset_email.html',
                    {
                        'user': user_obj,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)),
                        'token': default_token_generator.make_token(user_obj),
                        'protocol': 'https' if request.is_secure() else 'http',
                    },
                )
                #Debugging
                print("EMAIL_HOST_USER =", settings.EMAIL_HOST_USER)
                print("DEFAULT_FROM_EMAIL =", settings.DEFAULT_FROM_EMAIL)
                print("user_obj.email =", user_obj.email)
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_obj.email],
                    fail_silently=False,
                )

                return redirect('forgot_password_sent')

            else:
                return render(request, 'authentication/forgot_password.html', {
                    'form': form,
                    'error': 'No account found with this email address.'
                })

    return render(request, 'authentication/forgot_password.html', {'form': form})