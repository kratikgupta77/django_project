from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm
import json


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
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from .models import Message

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
        ).order_by("timestamp")  # Load messages in ascending order

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
            id__gt=last_message_id  # Fetch only new messages
        ).order_by("timestamp")

        messages_data = [
            {
                "id": msg.id,
                "text": msg.text,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "sender": msg.sender.username,
            }
            for msg in new_messages
        ]

        return JsonResponse({"messages": messages_data})

    return JsonResponse({"messages": []})
