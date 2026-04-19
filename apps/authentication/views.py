from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login

from apps.authentication.form import AdminLoginForm


def admin_dept_login(request):
    form = AdminLoginForm()

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)

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
                    else:
                        return render(request,'authentication/admin_dept_login.html',{
                          'form':form,
                          'error':'Access denied'
                        })

                else:
                    return redirect(request,'authentication/admin_dept_login.html',{
                        'form':form,
                        'error':'Invalid Credentials'
                    })

            else:
                return redirect(request,'authentication/admin_dept_login.html',{
                    'form':form,
                    'error':'Invalid Credentials'
                })

    return render(request, 'authentication/admin_dept_login.html',{
            'form':form,

        })

