from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
import csv

# Create your views here.
def Organizations(request):
    department_filter = request.GET.get('department', '')
    team_type_filter = request.GET.get('team_type', '')
    dependency_type_filter = request.GET.get('dependency_type', '')
    search_query = request.GET.get('search', '').strip()
    export_csv = request.GET.get('export', '').lower() == 'csv'

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT department_name
            FROM Department
            WHERE department_name IS NOT NULL AND department_name != ''
            ORDER BY department_name
            """
        )
        departments = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT DISTINCT development_focus_area
            FROM Team
            WHERE development_focus_area IS NOT NULL AND development_focus_area != ''
            ORDER BY development_focus_area
            """
        )
        team_types = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT DISTINCT dependency_type
            FROM TeamDependency
            WHERE dependency_type IS NOT NULL AND dependency_type != ''
            ORDER BY dependency_type
            """
        )
        dependency_types = [row[0] for row in cursor.fetchall()]

        query = [
            "SELECT t.team_id, dept.department_name AS department, ",
            "COALESCE(u.first_name || ' ' || u.last_name, dept.department_email) AS department_leader, ",
            "t.team_name, t.development_focus_area, dep.dependency_name, td.dependency_type, dep.criticality ",
            "FROM TeamDependency td ",
            "JOIN Team t ON td.team_id = t.team_id ",
            "LEFT JOIN Department dept ON t.department_id = dept.department_id ",
            "LEFT JOIN auth_user u ON dept.dept_head_user_id = u.id ",
            "JOIN Dependency dep ON td.dependency_id = dep.dependency_id ",
            "WHERE 1=1",
        ]
        params = []

        if department_filter:
            query.append("AND lower(dept.department_name) = lower(?)")
            params.append(department_filter)
        if team_type_filter:
            query.append("AND lower(t.development_focus_area) = lower(?)")
            params.append(team_type_filter)
        if dependency_type_filter:
            query.append("AND lower(td.dependency_type) = lower(?)")
            params.append(dependency_type_filter)
        if search_query:
            query.append(
                "AND (lower(dept.department_name) LIKE lower(?) OR lower(t.team_name) LIKE lower(?) OR lower(dep.dependency_name) LIKE lower(?))"
            )
            params.extend([f"%{search_query}%"] * 3)

        query.append("ORDER BY dept.department_name, department_leader, t.team_name, dep.dependency_name")
        sql = " ".join(query)
        if params and hasattr(cursor, 'cursor'):
            cursor.cursor.execute(sql, params)
        else:
            cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    unique_teams = sorted({row['team_name'] for row in rows if row['team_name']})
    unique_dependencies = sorted({row['dependency_name'] for row in rows if row['dependency_name']})

    # Handle CSV export
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="organization_data.csv"'

        writer = csv.writer(response)
        # Write header row
        writer.writerow(['Department', 'Department Leader', 'Team', 'Dependencies'])

        # Write data rows
        for row in rows:
            dependency_info = row['dependency_name'] or ''
            if row['dependency_type']:
                dependency_info += f" ({row['dependency_type']})"

            writer.writerow([
                row['department'] or '',
                row['department_leader'] or '',
                row['team_name'] or '',
                dependency_info
            ])

        return response

    return render(request, 'organizations/index.html', {
        'rows': rows,
        'departments': departments,
        'team_types': team_types,
        'dependency_types': dependency_types,
        'selected_department': department_filter,
        'selected_team_type': team_type_filter,
        'selected_dependency_type': dependency_type_filter,
        'search_query': search_query,
        'teams_count': len(unique_teams),
        'dependency_count': len(unique_dependencies),
        'total_rows': len(rows),
    }) 