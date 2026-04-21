from django.shortcuts import render




def management_dashboard(request):
    return render(request,"dashboard/management_dashboard.html")




def staff_dashboard(request):
    user_groups = list(request.user.groups.values_list('name', flat=True))

    context = {
        'user_groups': user_groups,
    }
    return render(request,"dashboard/staff_dashboard.html",context)

