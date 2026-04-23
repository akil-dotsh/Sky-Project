from telnetlib import STATUS

from django.shortcuts import render

from apps.dashboard.models import Team


def management_dashboard(request):

    return render(request,"dashboard/management_dashboard.html",{
        'active_team_count':get_active_team_count()
    })




def staff_dashboard(request):
    user_groups = list(request.user.groups.values_list('name', flat=True))

    context = {
        'user_groups': user_groups,
        'active_team_count': get_active_team_count()
    }
    return render(request,"dashboard/staff_dashboard.html",context)


def get_active_team_count():
    return Team.objects.filter(status='Active').count()