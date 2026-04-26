import os
import csv
import django

#Enviroment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sky_web_application.settings')
django.setup()

from apps.authentication.models import UserProfile
from django.contrib.auth.models import User
from apps.teams.models import Team, JiraProject, JiraBoard, ContactChannel, CodeRepository

#Check for existing db triggers
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
    print(cursor.fetchall())

#Main import function
def run_import():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'teams.csv')
    
    with open(file_path, mode='r', encoding='latin_1') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            team_name = row.get('Team Name', '').strip()
            leader_name = row.get('Team Leader', '').strip()
            ept = row.get('Department', '').strip()

            #Skip empty rows or malformed entries
            if not team_name or not leader_name or team_name.lower() == 'none':
                continue

            try:
                print(f"Importing Team: {team_name} | Leader: {leader_name}")
                #Create a system username based on the leader's name
                username = leader_name.lower().replace(" ","_")
                profile = None

                #Split full names for User fields
                name_parts = leader_name.split()
                f_name = name_parts[0] if name_parts else ""
                l_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                actual_team_obj, created = Team.objects.get_or_create(
                    name=team_name,
                    defaults={
                        'dept_head': row.get('Department Head', 'TBD'), 
                    }
                )
                
                user_obj, _ = User.objects.get_or_create(
                    username=username,
                   defaults={
                        'first_name': f_name, 
                        'last_name': l_name  
                    }
                )

                #Link the user to a profile and populate team specific metadata
                profile, created = UserProfile.objects.update_or_create(
                    user=user_obj,
                    defaults={
                        'team_id': team_name, 
                        'department': row.get('Department', ''),
                        'primary_skills': row.get('Key Skills & Technologies', ''),
                    }
                )
                count += 1
            except Exception as e:
                print(f"Error on row {count}: {e}")
                if profile:
                    #Captures secondary info associated with each team
                    if row.get('Jira board Link'):
                        JiraBoard.objects.get_or_create(
                            team=profile, 
                            board_url=row['Jira board Link'],
                            defaults={'name': f"{team_name} Board"}
                        )
                    if row.get('Jira Project Name'):
                        JiraProject.objects.get_or_create(
                            team=profile,
                            name=row['Jira Project Name']
                        )

                    if row.get('Project (codebase) (Github Repo)'):
                        CodeRepository.objects.get_or_create(
                            team=profile,
                            repo_url=row['Project (codebase) (Github Repo)']
                        )

                    if row.get('Slack Channels'):
                        ContactChannel.objects.get_or_create(
                            team=profile,
                            channel_id=row['Slack Channels'],
                            defaults={'channel_type': 'Slack'}
                        )

                count += 1
                print(f"Synced: {team_name}")

            except Exception as e:
                print(f"Error on row {count}: {e}")
    
    print(f"Success! Imported {count} teams and their associated data.")

if __name__ == '__main__':
    run_import()