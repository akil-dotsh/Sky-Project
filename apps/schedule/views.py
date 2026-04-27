import calendar
from datetime import date, datetime, timedelta, time as dt_time

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import MeetingForm
from .models import Meeting, MeetingParticipant


def _parse_focus_date(request):
    raw = request.GET.get('date')
    if raw:
        parsed = parse_date(raw)
        if parsed:
            return parsed
    return date.today()


def _build_month_grid(focus):
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    return cal.monthdatescalendar(focus.year, focus.month)


def _nav_dates(focus):
    first_of_month = focus.replace(day=1)
    prev_month = (first_of_month - timedelta(days=1)).replace(day=1)
    if focus.month == 12:
        next_month = date(focus.year + 1, 1, 1)
    else:
        next_month = date(focus.year, focus.month + 1, 1)
    return prev_month, next_month


def _week_range(focus):
    weekday = (focus.weekday() + 1) % 7  # 0 = Sunday
    start = focus - timedelta(days=weekday)
    end = start + timedelta(days=6)
    return start, end


def _as_local_dt(value):
    if value is None:
        return None
    return timezone.localtime(value) if timezone.is_aware(value) else value


def _upcoming(limit=5):
    now = timezone.now()
    return Meeting.objects.filter(start_datetime__gte=now).order_by('start_datetime')[:limit]


def _resolve_organiser(request):
    if request.user.is_authenticated:
        return request.user
    return User.objects.first()


def _base_context(request, view_name):
    focus = _parse_focus_date(request)
    return {
        'focus_date': focus,
        'today': date.today(),
        'active_view': view_name,
        'upcoming_meetings': _upcoming(),
    }


def schedule_home(request):
    return redirect('schedule:monthly')


def monthly_view(request):
    ctx = _base_context(request, 'monthly')
    focus = ctx['focus_date']
    prev_month, next_month = _nav_dates(focus)
    weeks = _build_month_grid(focus)

    month_meetings = Meeting.objects.filter(
        start_datetime__year=focus.year,
        start_datetime__month=focus.month,
    )
    by_day = {}
    for m in month_meetings:
        local = _as_local_dt(m.start_datetime)
        by_day.setdefault(local.date(), []).append(m)

    grid = []
    for week in weeks:
        row = []
        for day in week:
            row.append({
                'date': day,
                'in_month': day.month == focus.month,
                'is_today': day == ctx['today'],
                'meetings': by_day.get(day, []),
            })
        grid.append(row)

    ctx.update({
        'month_label': focus.strftime('%B %Y'),
        'weeks': grid,
        'prev_date': prev_month,
        'next_date': next_month,
        'weekday_labels': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'form': MeetingForm(organiser=_resolve_organiser(request)),
    })
    return render(request, 'schedule/monthly.html', ctx)


def weekly_view(request):
    ctx = _base_context(request, 'weekly')
    focus = ctx['focus_date']
    start, end = _week_range(focus)
    prev_date = start - timedelta(days=7)
    next_date = start + timedelta(days=7)

    days = [start + timedelta(days=i) for i in range(7)]
    hours = [f"{h:02d}:00" for h in range(8, 19)]

    range_start = datetime.combine(start, dt_time.min)
    range_end = datetime.combine(end, dt_time.max)
    if timezone.is_aware(timezone.now()):
        range_start = timezone.make_aware(range_start)
        range_end = timezone.make_aware(range_end)
    week_meetings = Meeting.objects.filter(start_datetime__range=(range_start, range_end))

    by_slot = {}
    for m in week_meetings:
        local = _as_local_dt(m.start_datetime)
        key = (local.date(), f"{local.hour:02d}:00")
        by_slot.setdefault(key, []).append(m)

    rows = []
    for hour in hours:
        cells = []
        for day in days:
            cells.append({
                'date': day,
                'hour': hour,
                'meetings': by_slot.get((day, hour), []),
                'is_today': day == ctx['today'],
            })
        rows.append({'hour': hour, 'cells': cells})

    ctx.update({
        'week_label': f"{start.strftime('%B')} {start.day} - {end.strftime('%B')} {end.day}, {end.year}",
        'days': [{'date': d, 'label': d.strftime('%a').upper(), 'is_today': d == ctx['today']} for d in days],
        'rows': rows,
        'prev_date': prev_date,
        'next_date': next_date,
        'form': MeetingForm(organiser=_resolve_organiser(request)),
    })
    return render(request, 'schedule/weekly.html', ctx)


def agenda_view(request):
    ctx = _base_context(request, 'agenda')
    meetings = Meeting.objects.all().order_by('start_datetime')
    
    ctx.update({
        'meetings': meetings,
        'meeting_count': meetings.count(),
        'form': MeetingForm(organiser=_resolve_organiser(request)),
    })
    return render(request, 'schedule/agenda.html', ctx)


def _agenda_error_context(form, extra=None):
    ctx = {
        'form': form,
        'meetings': Meeting.objects.all().order_by('start_datetime'),
        'meeting_count': Meeting.objects.count(),
        'active_view': 'agenda',
        'today': date.today(),
        'focus_date': date.today(),
        'upcoming_meetings': _upcoming(),
        'open_modal': True,
    }
    if extra:
        ctx.update(extra)
    return ctx


def _seed_participants(meeting):
    """Seed Meeting_Participant rows for a newly created meeting.

    Always adds the organiser (Accepted). For Individual meetings also adds
    the receiver (Invited). Team meetings leave team-wide expansion for the
    team-management flow.
    """
    now = timezone.now()
    rows = [(meeting.organiser_id, 'Accepted')]
    if meeting.meeting_type == 'Individual' and meeting.receiver_id:
        rows.append((meeting.receiver_id, 'Invited'))
    for user_id, status in rows:
        MeetingParticipant.objects.create(
            user_id=user_id,
            meeting=meeting,
            date=now,
            join_status=status,
        )


def create_meeting(request):
    organiser = _resolve_organiser(request)
    if request.method == 'POST':
        form = MeetingForm(request.POST, organiser=organiser)
        if form.is_valid():
            meeting = form.save(commit=False)
            if organiser is None:
                messages.error(request, 'No user available to organise the meeting. Please sign in.')
                return render(request, 'schedule/agenda.html', _agenda_error_context(form))
            meeting.organiser = organiser
            meeting.save()
            _seed_participants(meeting)
            messages.success(request, f'Meeting "{meeting.title}" scheduled.')
            return redirect(request.POST.get('next') or 'schedule:agenda')
        messages.error(request, 'Please fix the highlighted errors and try again.')
        return render(request, 'schedule/agenda.html', _agenda_error_context(form))
    return redirect('schedule:agenda')


def edit_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    organiser = _resolve_organiser(request)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting, organiser=organiser)
        if form.is_valid():
            form.save()
            messages.success(request, f'Meeting "{meeting.title}" updated.')
            return redirect(request.POST.get('next') or 'schedule:agenda')
        messages.error(request, 'Please fix the highlighted errors and try again.')
    else:
        form = MeetingForm(instance=meeting, organiser=organiser)

    ctx = _agenda_error_context(form, {'meeting': meeting, 'editing': True})
    return render(request, 'schedule/agenda.html', ctx)


def delete_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        title = meeting.title
        meeting.delete()
        messages.success(request, f'Meeting "{title}" deleted.')
    return redirect(request.POST.get('next') or 'schedule:agenda')
