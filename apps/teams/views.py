from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.authentication.models import UserProfile
from .models import Team, Dependency

#Directory view
def teams_list(request):
    teams = UserProfile.objects.filter(department__in=['xTV_Web', 'Native TVs'])

    query = request.GET.get('search') 
    if query:
        teams = teams.filter(
            Q(team_id__icontains=query) | 
            Q(primary_skills__icontains=query)
        )
    print(f"VIEW DEBUG: Sending {teams.count()} teams to the website")
    
    return render(request, 'teams/index.html', {'teams': teams, 'query':query})

#Detail view
def team_detail(request, user_id):
    #Fetch and match the profiles with the csv data
    profile = get_object_or_404(UserProfile, user_id=user_id)
    team_name = profile.team_id.strip()
    actual_team = Team.objects.filter(name__iexact=team_name).first()
    members = UserProfile.objects.filter(team_id=profile.team_id)
    #connects dependencies to their respective team leader
    raw_deps = Dependency.objects.filter(name__iexact=team_name)
    repo = profile.repositories.first()

    processed_deps = []
    for dep in raw_deps:
        #Cross reference the description with the Team model to find the leader
        dep_team_info = Team.objects.filter(name__iexact=dep.description).first()

        processed_deps.append({
            'target_team': dep.description,
            'type': dep.dep_type,
            'leader': dep_team_info.leader if dep_team_info else "TBD",
            'status': dep.status
        })

    focus_list = []
    if actual_team and actual_team.focus_areas:
        focus_list = [item.strip() for item in actual_team.focus_areas.split(',')]

    return render(request, 'teams/detail.html', {
        'team': profile, 
        'team_info': actual_team,
        'team_members': members,
        'dependencies':processed_deps,
        'focus_list': focus_list,
        'repo': repo,
    })

#Management view, allows to update the team bio
def update_bio(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user != team.user:
        return HttpResponseForbidden("You are not authorized to edit this bio.")

    if request.method == "POST":
        team.bio = request.POST.get('bio')
        team.save()
        return redirect('teams:detail', user_id=team.id) 
