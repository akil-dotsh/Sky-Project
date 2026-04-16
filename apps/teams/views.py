from django.shortcuts import render, get_object_or_404
from .models import Team

# 1. Shows all cards
def teams_list(request):
    teams = Team.objects.all()
    return render(request, 'teams/index.html', {'teams': teams})

# 2. Shows the specific "own page" for a clicked team
def team_detail(request, team_slug):
    team = get_object_or_404(Team, slug=team_slug)
    return render(request, 'teams/detail.html', {'team': team})