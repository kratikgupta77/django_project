from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, UserProfile, Group, GroupMessage
from .forms import UserUpdateForm, ProfileUpdateForm, GroupForm, GroupMessageForm
import json



from django.http import JsonResponse
from .models import Message
from django.core.files.base import ContentFile
import base64

from django.core.files.base import ContentFile

def receive_encrypted_file(request):
    if request.method == "POST":
        file_data = request.POST.get("file")
        file_name = request.POST.get("fileName")
        receiver_username = request.POST.get("receiver")

        if not file_data or not file_name or not receiver_username:
            return JsonResponse({"status": "error", "message": "Missing data"})

        sender = request.user
        receiver = User.objects.get(username=receiver_username)

        file_content = ContentFile(base64.b64decode(file_data), name=file_name)
        message = Message.objects.create(sender=sender, receiver=receiver, media=file_content)
        
        return JsonResponse({"status": "success", "message_id": message.id})
    
    return JsonResponse({"status": "error", "message": "Invalid request"})



# Existing views...
@login_required
def update_public_key(request):
    if request.method == "POST":
        data = json.loads(request.body)
        public_key = data.get("public_key")
        if public_key:
            profile = UserProfile.objects.get(user=request.user)
            profile.public_key = public_key
            profile.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        if "update_profile" in request.POST:
            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect("profile_view")
        elif "update_picture" in request.POST:
            picture_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
            if picture_form.is_valid():
                picture_form.save()
                return redirect("profile_view")
    else:
        form = UserUpdateForm(instance=request.user)
        picture_form = ProfileUpdateForm(instance=user_profile)
    return render(request, "profile_app/profile.html", {
        "form": form,
        "picture_form": picture_form,
        "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else "/static/default-profile.png",
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect("frontpage")

@login_required
def messages_view(request):
    users = User.objects.exclude(id=request.user.id)
    selected_user = None
    conversation = []
    receiver_id = request.GET.get("receiver")
    if receiver_id:
        selected_user = get_object_or_404(User, id=receiver_id)
        conversation = Message.objects.filter(
            Q(sender=request.user, receiver=selected_user) |
            Q(sender=selected_user, receiver=request.user)
        ).order_by("timestamp")
    context = {
        "users": users,
        "selected_user": selected_user,
        "messages": conversation,
    }
    return render(request, "profile_app/chat.html", context)


@login_required
def send_message(request):
    if request.method == "POST":
        sender = request.user
        receiver_id = request.POST.get("receiver")
        text = request.POST.get("text", "").strip()
        media = request.FILES.get("media")  # This will be populated from FormData
        
        if not receiver_id:
            return JsonResponse({"success": False, "error": "Receiver not specified."})
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        # Create the Message instance with media if provided.
        message = Message.objects.create(
            sender=sender, 
            receiver=receiver, 
            text=text, 
            media=media
        )
        
        return JsonResponse({
            "success": True,
            "message": {
                "id": message.id,
                "sender": sender.username,
                "text": message.text,
                "media_url": message.media.url if message.media else None,
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


import mimetypes

def fetch_messages(request):
    sender = request.user
    receiver_id = request.GET.get("receiver")
    last_message_id = request.GET.get("last_message_id", 0)

    if not receiver_id:
        return JsonResponse({"success": False, "error": "Receiver not specified."})

    receiver = get_object_or_404(User, id=receiver_id)

    messages = Message.objects.filter(
        sender__in=[sender, receiver], receiver__in=[sender, receiver], id__gt=last_message_id
    ).order_by("timestamp")

    messages_data = [
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "text": msg.text,
            "media_url": msg.media.url if msg.media else None,
        }
        for msg in messages
    ]

    return JsonResponse({"success": True, "messages": messages_data})
# --- New Views for Group Messaging ---

@login_required
def group_list_view(request):
    """List all groups and groups the user is a member of."""
    groups = Group.objects.all()
    user_groups = request.user.groups.all()
    return render(request, "profile_app/group_list.html", {
        "groups": groups,
        "user_groups": user_groups,
    })

@login_required
def create_group(request):
    """Create a new group."""
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            # Add creator as a member automatically.
            group.members.add(request.user)
            return redirect("group_detail", group_id=group.id)
    else:
        form = GroupForm()
    return render(request, "profile_app/create_group.html", {"form": form})

@login_required
def group_detail_view(request, group_id):
    """View group chat and members."""
    group = get_object_or_404(Group, id=group_id)
    # Only allow group members to view the chat.
    if request.user not in group.members.all():
        return redirect("group_list_view")
    messages = group.messages.all()
    message_form = GroupMessageForm()
    return render(request, "profile_app/group_chat.html", {
        "group": group,
        "messages": messages,
        "message_form": message_form,
    })
@login_required
def send_group_message(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST" and request.user in group.members.all():
        text = request.POST.get("text", "").strip()
        media = request.FILES.get("media")  # Get uploaded file

        if not text and not media:
            return JsonResponse({"success": False, "error": "Message cannot be empty"}, status=400)

        group_message = GroupMessage.objects.create(
            group=group,
            sender=request.user,
            text=text if text else None,
            media=media if media else None
        )

        return JsonResponse({
            "success": True,
            "message": {
                "id": group_message.id,
                "text": group_message.text or "",
                "media_url": group_message.media.url if group_message.media else None,
                "timestamp": group_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "sender": group_message.sender.username,
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def join_group(request, group_id):
    """Join a group."""
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.user)
    return redirect("group_detail", group_id=group.id)

@login_required
def leave_group(request, group_id):
    """Leave a group."""
    group = get_object_or_404(Group, id=group_id)
    group.members.remove(request.user)
    return redirect("group_list_view")

@login_required
def delete_group(request, group_id):
    """Delete a group if the user is the creator/admin."""
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.created_by:
        group.delete()
    return redirect("group_list_view")


@login_required
def fetch_group_messages(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        return JsonResponse({"messages": []})
        
    last_message_id = int(request.GET.get("last_message_id", 0))
    new_messages = group.messages.filter(id__gt=last_message_id).order_by("timestamp")

    messages_data = [{
        "id": msg.id,
        "text": msg.text or "",
        "media_url": msg.media.url if msg.media else None,
        "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "sender": msg.sender.username,
    } for msg in new_messages]

    return JsonResponse({"messages": messages_data})


@login_required
def group_detail_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        return redirect("group_list_view")
    messages = group.messages.all()
    last_message_id = messages.last().id if messages.exists() else 0
    message_form = GroupMessageForm()
    return render(request, "profile_app/group_chat.html", {
        "group": group,
        "messages": messages,
        "message_form": message_form,
        "last_message_id": last_message_id,
    })
