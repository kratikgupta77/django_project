from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, UserProfile, Group, GroupMessage
from .forms import UserUpdateForm, ProfileUpdateForm, GroupForm, GroupMessageForm
import json

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
        receiver_id = request.POST.get("receiver")
        text = request.POST.get("text", "").strip()
        if receiver_id and text:
            receiver = get_object_or_404(User, id=receiver_id)
            message = Message.objects.create(sender=request.user, receiver=receiver, text=text)
            return JsonResponse({
                "success": True,
                "message": {
                    "id": message.id,
                    "text": message.text,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "sender": message.sender.username,
                }
            })
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def fetch_messages(request):
    receiver_id = request.GET.get("receiver")
    last_message_id = request.GET.get("last_message_id", 0)
    if receiver_id:
        selected_user = get_object_or_404(User, id=receiver_id)
        new_messages = Message.objects.filter(
            Q(sender=request.user, receiver=selected_user) |
            Q(sender=selected_user, receiver=request.user),
            id__gt=last_message_id
        ).order_by("timestamp")
        messages_data = [{
            "id": msg.id,
            "text": msg.text,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "sender": msg.sender.username,
        } for msg in new_messages]
        return JsonResponse({"messages": messages_data})
    return JsonResponse({"messages": []})

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
    """Send a message in a group."""
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST" and request.user in group.members.all():
        form = GroupMessageForm(request.POST)
        if form.is_valid():
            group_message = form.save(commit=False)
            group_message.group = group
            group_message.sender = request.user
            group_message.save()
            return JsonResponse({
                "success": True,
                "message": {
                    "id": group_message.id,
                    "text": group_message.text,
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
    """
    Return new group messages posted after the given last_message_id.
    """
    group = get_object_or_404(Group, id=group_id)
    # Optional: Ensure the user is a member of this group.
    if request.user not in group.members.all():
        return JsonResponse({"messages": []})
        
    last_message_id = int(request.GET.get("last_message_id", 0))
    new_messages = group.messages.filter(id__gt=last_message_id).order_by("timestamp")
    messages_data = [{
        "id": msg.id,
        "text": msg.text,
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
