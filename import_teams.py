import os
import csv
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sky_web_application.settings')
django.setup()

from apps.teams.models import Team

def run_import():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_dir, 'teams.csv')
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            
            Team.objects.get_or_create(
                name=row['Team Name'],
                defaults={
                    'leader': row['Team Leader'],
                    'department': row['Department'],
                    'dept_head': row['Department Head'],
                    'jira_project': row['Jira Project Name'],
                    'focus_areas': row['Development Focus Areas'],
                    'tech_stack': row['Key Skills & Technologies'],
                }
            )
            count += 1
    print(f"Success! Imported {count} teams from the Sky Registry.")

if __name__ == '__main__':
    run_import()