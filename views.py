import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message
from apps.teams.models import Team
from django.http import JsonResponse

def get_dev_user():
    return User.objects.filter(username="dev").first()

def inbox(request):
    user = request.user if request.user.is_authenticated else None

    messages = Message.objects.filter(
        recipient=user,
        recipient_type='Individual',
        is_draft=False
    ) if user else Message.objects.none()

    return render(request, 'messaging/inbox.html', {'messages': messages})

def messaging(request):

    print("USER:", request.user)
    print("AUTH:", request.user.is_authenticated)

    sender = User.objects.filter(username="dev").first()
    
    if request.method == "POST":

        sender = request.user
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        action = request.POST.get("action")
        attachment = request.FILES.get("attachment")
        excel_file = request.FILES.get("excel_file")

        sent_time = timezone.now()
        status = "Sent" if action == "send" else "Draft"

        # =========================
        # EXCEL BULK SEND
        # =========================
        if excel_file:

            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():

                recipient_value = str(row.get("recipient", "")).strip()
                team_name = str(row.get("team", "")).strip()
                row_subject = row.get("subject", subject)
                row_body = row.get("body", body)

                # USER
                if recipient_value:

                    user = User.objects.filter(
                        email=recipient_value
                    ).first() or User.objects.filter(
                        username=recipient_value
                    ).first()

                    if user:
                        Message.objects.create(
                            sender=sender,
                            recipient=user,
                            recipient_type="Individual",
                            subject=row_subject,
                            body=row_body,
                            attachment=attachment,
                            status="Sent",
                            sent_at=sent_time,
                            is_draft=False   # 👈 ADD HERE
                        )

                # TEAM
                elif team_name:

                    team = Team.objects.filter(name=team_name).first()

                    if team:

                        for member in team.members.all():

                            Message.objects.create(
                                sender=sender,
                                recipient=member,
                                recipient_team=team,
                                recipient_type="Team",
                                subject=row_subject,
                                body=row_body,
                                attachment=attachment,
                                status="Sent",
                                sent_at=sent_time,
                                is_draft=False,
                            )

            return redirect("messaging:sent")

        # =========================
        # SINGLE SEND
        # =========================
        recipient_username = request.POST.get("recipient")
        team_name = request.POST.get("teams")

        if recipient_username:

            user = User.objects.filter(
                email=recipient_username
            ).first() or User.objects.filter(
                username=recipient_username
            ).first()

            if user:
                Message.objects.create(
                    sender=sender,
                    recipient=user,
                    recipient_type="Individual",
                    subject=subject,
                    body=body,
                    attachment=attachment,
                    status=status,
                    sent_at=sent_time
                )

        elif team_name:

            team = Team.objects.filter(name=team_name).first()

            if team:

                for member in team.members.all():

                    Message.objects.create(
                        sender=sender,
                        recipient=member,
                        recipient_type="Team",
                        subject=subject,
                        body=body,
                        attachment=attachment,
                        status=status,
                        sent_at=sent_time
                    )

        return redirect("messaging:sent")

    return render(request, "messaging/messaging.html")

def sent(request):

    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    messages = Message.objects.filter(
        sender=user,
        is_draft=False
    ).order_by('-sent_at')

    return render(request, 'messaging/sent.html', {'messages': messages})

def draft(request):

    if request.method == "POST":

        recipient_username = request.POST.get("recipient")
        team_name = request.POST.get("teams")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        attachment = request.FILES.get("attachment")

        user = None
        team = None

        if recipient_username:
            user = User.objects.filter(
                email=recipient_username
            ).first() or User.objects.filter(
                username=recipient_username
            ).first()

        if team_name:
            team = Team.objects.filter(name=team_name).first()

        Message.objects.create(
            sender=get_dev_user(),
            recipient=user if user else None,
            recipient_team=team if team else None,
            recipient_type="Individual" if user else "Team" if team else "",
            subject=subject,
            body=body,
            attachment=attachment,
            is_draft=True,
            status="Queued",
            sent_at=None
        )

        return redirect("messaging:draft")

    # ✅ THIS MUST ALWAYS RUN FOR GET
    messages = Message.objects.filter(
        is_draft=True
    ).order_by('-message_id')

    return render(request, 'messaging/draft.html', {'messages': messages})

def message_detail(request, id):
    message = get_object_or_404(Message, id=id)

    if request.user.is_authenticated:

        if message.sender and request.user != message.sender and request.user != message.recipient:
           return redirect('inbox')

        if request.user == message.recipient and message.read_at is None:
           message.read_at = timezone.now()
           message.status = 'Read'
           message.save()

    return render(request, 'message_detail.html', {'message': message})

def autosave_draft(request):
    if request.method == "POST":

        sender = User.objects.filter(username="dev").first()

        draft_id = request.POST.get("draft_id")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        recipient_username = request.POST.get("recipient")

        if not subject and not body:
            return JsonResponse({})

        user = None
        if recipient_username:
            user = User.objects.filter(
                email=recipient_username
            ).first() or User.objects.filter(
                username=recipient_username
            ).first()

        # UPDATE existing draft
        if draft_id:
            message = Message.objects.filter(message_id=draft_id).first()

            if message:
                message.subject = subject
                message.body = body
                message.recipient = user
                message.save()

                return JsonResponse({"draft_id": message.message_id})

        # CREATE new draft
        message = Message.objects.create(
        sender=sender,
        recipient=user,
        recipient_type="Individual" if user else "",
        subject=subject,
        body=body,
        is_draft=True,
        status="Queued",
        sent_at=None
        )

        return JsonResponse({"draft_id": message.message_id})

    return JsonResponse({"error": "Invalid request"}, status=400)