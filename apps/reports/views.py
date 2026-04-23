from itertools import count
from lib2to3.fixes.fix_input import context
from tkinter.font import names
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Q

from .models import Report


# Create your views here.

def admin_report(request):
    last_30_days = timezone.now() - timezone.timedelta(days=30)
    total_reports_count=Report.objects.filter(
        created_at__gte=last_30_days,
        is_scheduled=False
    ).count()

    scheduled_reports_count=Report.objects.filter(
        is_scheduled=True,
    ).count()

    search_query=request.GET.get('search','').strip()
    status_filter=request.GET.get('status','').strip()
    reports_queryset=Report.objects.filter(
        is_scheduled=False,
    ).order_by('created_at')

    if search_query:
        reports_queryset=reports_queryset.filter(
            Q(report_name__icontains=search_query) |
            Q(report_type__icontains=search_query) |
            Q(scope__icontains=search_query)
        )

    elif status_filter:
        reports_queryset=reports_queryset.filter(
            status=status_filter,
        )
    last_15_reports=reports_queryset[:15]

    context = {

        'total_reports_count': total_reports_count,
        'scheduled_reports_count': scheduled_reports_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'last_15_reports': last_15_reports,
    }
    return render(request, 'reports/admin_report.html',context)


