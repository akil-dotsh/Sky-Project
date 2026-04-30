from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message
from apps.teams.models import Team
from django.http import JsonResponse
from django.contrib import messages


def get_dev_user():
    return User.objects.filter(username="dev").first()


# Manages inbox
def inbox(request):
    user = request.user if request.user.is_authenticated else None

    inbox_messages = Message.objects.filter(
        recipient=user,
        recipient_type='Individual',
        sent_at__isnull=False,
    ) if user else Message.objects.none()

    return render(request, 'messaging/inbox.html', {'inbox_messages': inbox_messages})


def messaging(request):
    sender = request.user if request.user.is_authenticated else get_dev_user()

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        action = request.POST.get("action")
        attachment = request.FILES.get("attachment")

        recipient_username = request.POST.get("recipient", "").strip()
        team_name = request.POST.get("teams", "").strip()

        is_draft = (action == "draft")
        # Status must match the DB CHECK constraint:
        # ('Queued','Sent','Delivered','Read','Failed'). Drafts stay Queued.
        status = "Queued" if is_draft else "Sent"
        sent_time = None if is_draft else timezone.now()

        messages_created = 0

        def create_individual_message(recipient):
            nonlocal messages_created
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                recipient_type="Individual",
                subject=subject,
                body=body,
                attachment=attachment,
                status=status,
                sent_at=sent_time,
            )
            messages_created += 1

        def create_team_message(team):
            nonlocal messages_created
            Message.objects.create(
                sender=sender,
                recipient_team=team,
                recipient_type="Team",
                subject=subject,
                body=body,
                attachment=attachment,
                status=status,
                sent_at=sent_time,
            )
            messages_created += 1

        if recipient_username:
            user = User.objects.filter(email=recipient_username).first() \
                or User.objects.filter(username=recipient_username).first()

            if user:
                create_individual_message(user)
            else:
                # External recipients aren't supported by the DB schema
                # (recipient_type CHECK only allows Individual / Team).
                messages.error(request, "Recipient not found")

        if team_name:
            team = Team.objects.filter(name=team_name).first()
            if team:
                create_team_message(team)
            else:
                messages.error(request, "Team not found")

        if messages_created == 0:
            messages.error(request, "No message was sent")
            return redirect("messaging:messaging")

        if is_draft:
            messages.success(request, "Draft saved")
            return redirect("messaging:draft")

        messages.success(request, "Message sent")
        return redirect("messaging:sent")

    return render(request, "messaging/messaging.html")


# records sent messages
def sent(request):
    user = request.user if request.user.is_authenticated else None

    sent_messages = Message.objects.filter(
        sender=user,
        sent_at__isnull=False,
    ).order_by('-sent_at') if user else Message.objects.none()

    return render(request, 'messaging/sent.html', {'sent_messages': sent_messages})


# list of draft messages
def draft(request):
    sender = request.user if request.user.is_authenticated else get_dev_user()

    if request.method == "POST":
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        attachment = request.FILES.get("attachment")

        recipient_username = request.POST.get("recipient")
        team_name = request.POST.get("teams")

        user = None
        team = None
        if recipient_username:
            user = User.objects.filter(email=recipient_username).first() \
                or User.objects.filter(username=recipient_username).first()
        if team_name:
            team = Team.objects.filter(name=team_name).first()

        Message.objects.create(
            sender=sender,
            recipient=user,
            recipient_team=team,
            recipient_type="Individual" if user else "Team",
            subject=subject,
            body=body,
            attachment=attachment,
            status="Queued",
            sent_at=None,
        )

        return redirect("messaging:draft")

    draft_messages = Message.objects.filter(
        sender=sender,
        sent_at__isnull=True,
    ).order_by('-message_id') if sender else Message.objects.none()

    return render(request, 'messaging/draft.html', {'draft_messages': draft_messages})


# the messages themselves and their details.
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)

    if request.user.is_authenticated:
        if message.sender and request.user != message.sender and request.user != message.recipient:
            return redirect('messaging:inbox')

        if request.user == message.recipient and message.read_at is None:
            message.read_at = timezone.now()
            message.status = 'Read'
            message.save()

    return render(request, 'messaging/message_detail.html', {'draft_message': message})


# auto saves drafts
def autosave_draft(request):
    if request.method == "POST":
        sender = request.user if request.user.is_authenticated else get_dev_user()

        draft_id = request.POST.get("draft_id")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        recipient_username = request.POST.get("recipient")

        if not subject and not body:
            return JsonResponse({})

        user = None
        if recipient_username:
            user = User.objects.filter(email=recipient_username).first() \
                or User.objects.filter(username=recipient_username).first()

        # UPDATE existing draft
        if draft_id:
            message = Message.objects.filter(message_id=draft_id).first()
            if message:
                message.subject = subject
                message.body = body
                message.recipient = user
                message.save()
                return JsonResponse({"draft_id": message.message_id})

        # creates new draft (must satisfy DB CHECK constraints)
        if user is None:
            # No recipient yet — DB rejects null recipient with Individual.
            # Skip persistence until the user picks someone.
            return JsonResponse({})

        message = Message.objects.create(
            sender=sender,
            recipient=user,
            recipient_type="Individual",
            subject=subject,
            body=body,
            status="Queued",
            sent_at=None,
        )

        return JsonResponse({"draft_id": message.message_id})

    return JsonResponse({"error": "Invalid request"}, status=400)


# deletes messages in inbox
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk)

    if request.user != message.sender and request.user != message.recipient:
        return redirect('messaging:inbox')

    if request.method == "POST":
        message.delete()
        return redirect('messaging:inbox')

    return redirect('messaging:inbox')


# deletes drafts
def delete_draft(request, pk):
    draft = get_object_or_404(Message, message_id=pk)

    if request.method == "POST":
        draft.delete()

    return redirect("messaging:draft")
