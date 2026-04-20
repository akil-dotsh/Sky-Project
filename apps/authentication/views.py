from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login

from apps.authentication.form import LoginForm, RegistrationForm
from apps.authentication.models import UserProfile


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
                        return redirect('admin:index')
                    # Only Team leader and Developer
                    elif user.groups.filter(name='Team Leader').exists() or user.groups.filter(name='Developer').exists():
                        login(request,user)
                        return redirect('User Dashboard')
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

