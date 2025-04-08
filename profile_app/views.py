from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import random
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q

import zlib
from cryptography.fernet import Fernet

from profile_app import models
from .models import Message, UserProfile, Group, GroupMessage
from .forms import UserUpdateForm, ProfileUpdateForm, GroupForm, GroupMessageForm,OTPVerificationForm
import json
from django.conf import settings

import random
from django.core.mail import send_mail

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import traceback

from django.http import JsonResponse
from .models import Message
from django.core.files.base import ContentFile
import base64

from django.core.files.base import ContentFile


count =0 #useless
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
    users = User.objects.exclude(id=request.user.id).filter(is_active=True, is_staff=False, is_superuser=False)
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



# key = Fernet.generate_key()
# fernet = Fernet(b'qHImXvD7qzhdQ0gB4Dj5V4T5z7NYzZ4FtZ1ucxvQjrs=')  # Use from user's key ideally

# def compress_and_encrypt_media(file):   
#     compressed_data = zlib.compress(file.read())
#     encrypted_data = fernet.encrypt(compressed_data)
#     return encrypted_data

# def decrypt_and_decompress_media(blob):
#     decrypted_data = fernet.decrypt(blob)
#     decompressed_data = zlib.decompress(decrypted_data)
#     return decompressed_data



def get_public_key(request, username):
    try:
        user = User.objects.get(username=username)
        profile = user.userprofile

        if not profile.public_key:
            return JsonResponse({'error': 'Public key not found for user'}, status=404)

        return JsonResponse({'public_key': profile.public_key})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)


# views.py
from django.conf import settings
from threading import Thread
from django.core.mail import send_mail

def send_async_email(subject, message, from_email, recipient_list):
    Thread(target=send_mail, args=(subject, message, from_email, recipient_list), kwargs={'fail_silently': False}).start()
import random
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


@login_required
def send_delete_otp(request):
    if request.method == "POST":
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        request.session['delete_otp'] = otp
        request.session['delete_user_id'] = request.user.id

        send_async_email(
            "OTP to Delete Your Account",
            f"Your OTP to delete your account is: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email]
        )
        return redirect('verify_delete_otp')


@login_required
def verify_delete_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if entered_otp == request.session.get("delete_otp"):
            try:
                user = User.objects.get(id=request.session.get("delete_user_id"))
                user.delete()
                request.session.pop("delete_otp", None)
                request.session.pop("delete_user_id", None)
                return redirect('login')
            except User.DoesNotExist:
                return render(request, "profile_app/enter_otp_delete.html", {"error": "User not found."})
        else:
            return render(request, "profile_app/enter_otp_delete.html", {"error": "Invalid OTP."})

    return render(request, "profile_app/enter_otp_delete.html")


@login_required
def send_reset_otp(request):
    if request.method == "POST":
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        request.session['reset_otp'] = otp
        request.session['otp_user_id'] = request.user.id

        send_async_email(
            "Your OTP for Password Reset",
            f"Your OTP is: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email]
        )
        return redirect('verify_reset_otp')


@login_required
def verify_reset_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")

        if entered_otp == request.session.get("reset_otp"):
            try:
                user = User.objects.get(id=request.session.get("otp_user_id"))
                user.password = make_password(new_password)
                user.save()

                request.session.pop("reset_otp", None)
                request.session.pop("otp_user_id", None)
                return redirect('login')
            except User.DoesNotExist:
                return render(request, "profile_app/verify_otp.html", {"error": "User not found."})
        else:
            return render(request, "profile_app/verify_otp.html", {"error": "Invalid OTP."})

    return render(request, "profile_app/verify_otp.html")

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
