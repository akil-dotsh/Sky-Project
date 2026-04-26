import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.formats import date_format

from apps.reports.models import ResourceLink
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from apps.dashboard.models import Team
from .models import Report, JiraProject, JiraBoard,ResourceLink


def admin_report(request):
    last_30_days = timezone.now() - timezone.timedelta(days=30)

    total_reports_count = Report.objects.filter(
        created_at__gte=last_30_days,
        is_scheduled=False
    ).count()

    scheduled_reports_count = Report.objects.filter(
        is_scheduled=True
    ).count()

    search_query = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "").strip()

    reports_queryset = Report.objects.filter(
        is_scheduled=False
    ).order_by("-created_at")

    if search_query:
        reports_queryset = reports_queryset.filter(
            Q(report_name__icontains=search_query) |
            Q(report_type__icontains=search_query) |
            Q(scope__icontains=search_query)
        )

    if status_filter:
        reports_queryset = reports_queryset.filter(
            status=status_filter
        )

    last_15_reports = reports_queryset[:15]

    share_report_count= ResourceLink.objects.filter(
        resource_type='report',
    ).count()

    context = {
        "total_reports_count": total_reports_count,
        "scheduled_reports_count": scheduled_reports_count,
        "search_query": search_query,
        "status_filter": status_filter,
        "last_15_reports": last_15_reports,
        "teams": Team.objects.all().order_by("team_name"),
        "share_report_count": share_report_count,
    }

    return render(request, "reports/admin_report.html", context)


def report_generate(request):
    """
    Generate a PDF report using ReportLab.

    Note:
    Team is connected to JiraProject using Team.jira_project_id.
    JiraProject is connected to JiraBoard using JiraProject.jiraBoard_id.

    Relationship:
    Team.jira_project_id -> JiraProject.jira_project_id
    JiraProject.jiraBoard_id -> JiraBoard.jiraBoard_id
    """

    teams = Team.objects.all().order_by("team_name")

    if request.method == "POST":
        # Read submitted form values
        report_type = request.POST.get("report_type")
        department = request.POST.get("department")
        team_id = request.POST.get("team_id")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        compare_previous = request.POST.get("compare_previous") == "on"

        # Get selected team safely
        selected_team = get_object_or_404(Team, team_id=team_id)

        # Get Jira project connected to the selected team
        jira_project = None

        if selected_team.jira_project_id:
            jira_project = JiraProject.objects.filter(
                jira_project_id=selected_team.jira_project_id
            ).first()

        # Get Jira board connected to the Jira project
        jira_board = None

        if jira_project:
            jira_board = JiraBoard.objects.filter(
                jiraBoard_id=jira_project.jiraBoard_id
            ).first()

        # Create safe PDF file name
        safe_team_name = selected_team.team_name.lower().replace(" ", "_")
        generated_timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{safe_team_name}_report_{generated_timestamp}.pdf"

        # Create media/reports folder if it does not exist
        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        # Full PDF file path
        pdf_path = os.path.join(reports_dir, file_name)

        # URL stored in the database
        report_url = f"{settings.MEDIA_URL}reports/{file_name}"

        # -----------------------------------------------------
        # Generate PDF using ReportLab
        # -----------------------------------------------------

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        story = []

        # Report title
        title = f"{report_type} - {selected_team.team_name}"

        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 12))

        # Generated details
        generated_at = timezone.now().strftime("%d %B %Y, %I:%M %p")

        story.append(
            Paragraph(
                f"Generated on {generated_at} | Period: {from_date} to {to_date}",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 20))

        # Summary section
        story.append(Paragraph("Summary", styles["Heading2"]))

        summary_data = [
            ["Team", selected_team.team_name],
            ["Team Status", selected_team.status],
            [
                "Jira Project",
                jira_project.project_name if jira_project else "Not assigned",
            ],
        ]

        summary_table = Table(summary_data, colWidths=[160, 320])

        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1e3a8a")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbeafe")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Team Information
        story.append(Paragraph("1. Team Information", styles["Heading2"]))

        team_data = [
            ["Team Name", selected_team.team_name],
            ["Status", selected_team.status],
            ["Purpose", selected_team.purpose or "N/A"],
            ["Responsibility", selected_team.responsibility or "N/A"],
            ["Description", selected_team.description or "N/A"],
            ["Team Email", selected_team.team_email or "N/A"],
            ["On-call Contact", selected_team.on_call_contact or "N/A"],
            ["Location", selected_team.location or "N/A"],
            ["Development Focus Area", selected_team.development_focus_area or "N/A"],
            ["Key Skills / Technology", selected_team.key_skills_technology or "N/A"],
            ["Software Owned", selected_team.software_owned or "N/A"],
            ["Agile Practice", selected_team.agile_practice or "N/A"],
            ["Daily Standup Time", selected_team.daily_standup_time or "N/A"],
            ["Team Wiki URL", selected_team.team_wiki_url or "N/A"],
            ["Last Reviewed At", selected_team.last_reviewed_at or "N/A"],
            ["Created At", selected_team.created_at or "N/A"],
            ["Updated At", selected_team.updated_at or "N/A"],
        ]

        team_table = Table(team_data, colWidths=[170, 310])

        team_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        story.append(team_table)
        story.append(Spacer(1, 20))

        # Jira Project Information
        story.append(Paragraph("2. Jira Project Information", styles["Heading2"]))

        if jira_project:
            jira_project_data = [
                ["Project Name", jira_project.project_name],
                ["Description", jira_project.description or "N/A"],
                ["Project Type", jira_project.project_type],
                ["Status", jira_project.status],
                ["Created At", jira_project.created_at or "N/A"],
            ]
        else:
            jira_project_data = [
                ["Jira Project", "No Jira project is assigned to this team."]
            ]

        jira_project_table = Table(jira_project_data, colWidths=[170, 310])

        jira_project_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        story.append(jira_project_table)
        story.append(Spacer(1, 20))

        # Jira Board Information
        story.append(Paragraph("3. Jira Board Information", styles["Heading2"]))

        if jira_board:
            jira_board_data = [
                ["Board Name", jira_board.board_name],
                ["Board Type", jira_board.board_type],
                ["Is Active", "Yes" if jira_board.is_active else "No"],
                ["Created At", jira_board.created_at or "N/A"],
                ["Updated At", jira_board.updated_at or "N/A"],
            ]
        else:
            jira_board_data = [
                ["Jira Board", "No Jira board information is available for this team."]
            ]

        jira_board_table = Table(jira_board_data, colWidths=[170, 310])

        jira_board_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        story.append(jira_board_table)
        story.append(Spacer(1, 20))

        # Recommendation
        story.append(Paragraph("4. Recommendation", styles["Heading2"]))

        story.append(
            Paragraph(
                "This report provides a team-level operational and Jira status overview. "
                "Teams with inactive status, missing Jira projects, or inactive Jira boards "
                "should be reviewed by management.",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 25))

        story.append(
            Paragraph(
                "Sky Reporting System — Generated automatically from Team, JiraProject and JiraBoard data.",
                styles["Italic"],
            )
        )

        # Build and save the PDF file
        doc.build(story)

        # Save generated report record
        Report.objects.create(
            report_name=title,
            report_type=report_type,
            report_format="PDF",
            status="Successful",
            scope=selected_team.team_name,
            department=department,
            from_date=from_date,
            to_date=to_date,
            compare_previous=compare_previous,
            report_url=report_url,
            created_at=timezone.now(),
            team_id=selected_team.team_id,
            is_scheduled=False,
            last_run_at=timezone.now(),
            next_run_at=None,
            schedule_frequency=None,
        )

        messages.success(request, "Report generated successfully.")

        return redirect("admin_report")

    return render(
        request,
        "reports/admin_report.html",
        {
            "teams": teams,
        },
    )


def share_report(request):
    """
    Share a generated report with one or more teams.

    Creating ResourceLink rows so team members can access
    the report through their team_id.
    """

    if request.method == "POST":
        report_id = request.POST.get("report_id")
        team_ids = request.POST.getlist("team_ids")
        permission = request.POST.get("permission")
        message = request.POST.get("message")

        # Get selected report safely
        report = get_object_or_404(Report, report_id=report_id)

        # Only share if the report has a generated PDF URL
        if not report.report_url:
            messages.error(request, "This report does not have a PDF URL to share.")
            return redirect("admin_report")

        # Create one ResourceLink record per selected team
        for team_id in team_ids:
            ResourceLink.objects.create(
                resource_type="report",
                documentation=f"Shared report: {report.report_name}",
                description=message,
                resource_value=permission,
                report_url=report.report_url,
                created_at=timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                team_id=team_id
            )

        messages.success(request, "Report shared successfully.")

    return redirect("admin_report")


@login_required
def user_reports(request):
    """
    Display reports shared with the logged-in user's team.

    ResourceLink stores shared report links.
    A normal user can only see reports where their team_id matches
    ResourceLink.team_id.
    """

    search_query = request.GET.get("search", "").strip()
    category_filter = request.GET.get("category", "").strip()

    user_profile = getattr(request.user, "userprofile", None)

    if not user_profile or not user_profile.team_id:
        shared_reports = ResourceLink.objects.none()
    else:
        shared_reports = ResourceLink.objects.filter(
            resource_type="report",
            team_id=user_profile.team_id
        ).order_by("-created_at")

    if search_query:
        shared_reports = shared_reports.filter(
            Q(resource_value__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        shared_reports = shared_reports.filter(
            resource_value__icontains=category_filter
        )

    shared_reports_count = shared_reports.count()
    last_shared_report = shared_reports.first()

    context = {
        "shared_reports": shared_reports,
        "shared_reports_count": shared_reports_count,
        "last_shared_report": last_shared_report,
        "search_query": search_query,
        "category_filter": category_filter,
    }

    return render(request, "reports/user_reports.html", context)