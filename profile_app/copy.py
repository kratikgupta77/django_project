from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from .models import Message, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm, MessageForm

from django.shortcuts import get_object_or_404, render

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
    receiver_id = request.GET.get("receiver")  # Get selected chat user
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver_id=receiver_id)) | 
        (Q(sender_id=receiver_id) & Q(receiver=request.user))
    ).order_by("timestamp")  # Fetch messages between users

    users = User.objects.exclude(id=request.user.id)  # Show other users
    return render(request, "profile_app/chat.html", {"users": users, "messages": messages})

@login_required
def send_message(request):
    """Handles sending messages between users."""
    if request.method == "POST":
        receiver_id = request.POST.get("receiver")
        # message_text = request.POST.get("message")
        message_text = request.POST.get('message', '').strip()

        if receiver_id and message_text.strip():
            receiver = get_object_or_404(User, id=receiver_id)
            Message.objects.create(sender=request.user, receiver=receiver, text=message_text)

    return redirect("messages_view")








# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import logout
# from django.contrib.auth.models import User
# from django.http import JsonResponse
# from django.db.models import Q
# from .models import Message, UserPrzofile
# from .forms import UserUpdateForm, ProfileUpdateForm, MessageForm

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, render
# from django.db.models import Q
# from .models import Message

# @login_required
# def chat_view(request, receiver_username):
#     receiver = get_object_or_404(User, username=receiver_username)
    
#     messages = Message.objects.filter(
#         Q(sender=request.user, receiver=receiver) |
#         Q(sender=receiver, receiver=request.user)
#     ).order_by("timestamp")

#     return render(request, "profile_app/chat.html", {
#         "receiver": receiver,
#         "messages": messages
#     })


# def send_message(request):
#     if request.method == "POST":
#         sender = request.user
#         receiver_username = request.POST.get('receiver_username', '').strip().lower()

#         print(f"Received username: {receiver_username}")  # Debugging

#         if not receiver_username:
#             return JsonResponse({"status": "error", "message": "Receiver username missing"}, status=400)

#         try:
#             receiver = User.objects.get(username__iexact=receiver_username)
#             print(f"Found user: {receiver}")  # Debugging
#         except User.DoesNotExist:
#             print("User not found")  # Debugging
#             return JsonResponse({"status": "error", "message": "User not found"}, status=404)

#         message_content = request.POST.get('message', '')
#         message = Message.objects.create(sender=sender, receiver=receiver, text=message_content)
#         return JsonResponse({"status": "success", "message_id": message.id})

#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# @login_required
# def messages_view(request, receiver_username=None):
#     users = User.objects.exclude(id=request.user.id)
#     selected_user = None
#     messages = []

#     if receiver_username:
#         selected_user = get_object_or_404(User, username=receiver_username)
#         messages = Message.objects.filter(
#             Q(sender=request.user, receiver=selected_user) |
#             Q(sender=selected_user, receiver=request.user)
#         ).order_by("timestamp")

#         receiver_profile = UserProfile.objects.get(user=request.user)
#         private_key = receiver_profile.get_private_key()
#         for msg in messages:
#             msg.decrypted_content = msg.decrypt_message(private_key)

#     return render(request, "profile_app/chat.html", {
#         "users": users,
#         "selected_user": selected_user,
#         "messages": messages
#     })

# # @login_required
# # def send_message(request):
# #     if request.method == "POST":
# #         sender = request.user
# #         receiver_id = request.POST.get("receiver")
# #         message_content = request.POST.get("content")

# #         receiver = get_object_or_404(User, id=receiver_id)

# #         message = Message(sender=sender, receiver=receiver)
# #         message.encrypt_message(message_content)
# #         message.save()

# #         return JsonResponse({"status": "Message sent and encrypted!"})



# # 
# # 
# # 
# # from django.shortcuts import render, redirect
# # from django.contrib.auth.decorators import login_required
# # from django.contrib.auth import logout
# # from django.contrib.auth.models import User

# # from .models import Message, UserProfile
# # from django.shortcuts import render, redirect
# # from django.contrib.auth.decorators import login_required
# # from .models import UserProfile
# # from .forms import UserUpdateForm,ProfileUpdateForm,MessageForm
# # from django.shortcuts import get_object_or_404
# # from django.db.models import Q

# # # @login_required
# # # def messages_view(request):
# # #     users = User.objects.exclude(id=request.user.id)  # List all users except the current one
# # #     selected_user = None
# # #     messages = []

# # #     if request.method == "POST":
# # #         selected_user_id = request.POST.get("receiver")
# # #         content = request.POST.get("message")

# # #         if selected_user_id and content:
# # #             selected_user = User.objects.get(id=selected_user_id)
# # #             message = Message(sender=request.user, receiver=selected_user, encrypted_content=content)
# # #             message.save()
# # #             return redirect("messages")

# # #     if "receiver" in request.GET:
# # #         selected_user_id = request.GET["receiver"]
# # #         selected_user = User.objects.get(id=selected_user_id)
# # #         messages = Message.objects.filter(
# # #             sender__in=[request.user, selected_user], receiver__in=[request.user, selected_user]
# # #         ).order_by("timestamp")

# # #         # Decrypt messages before sending to template
# # #         receiver_profile = UserProfile.objects.get(user=request.user)
# # #         private_key = receiver_profile.get_private_key()
# # #         for msg in messages:
# # #             msg.decrypted_content = msg.decrypt_message(private_key)

# # #     return render(request, "profile_app/messages.html", {"users": users, "selected_user": selected_user, "messages": messages})


# # @login_required
# # def profile_view(request):
# #     user_profile, created = UserProfile.objects.get_or_create(user=request.user)

# #     if request.method == "POST":
# #         if "update_profile" in request.POST:  # Updating username and email
# #             form = UserUpdateForm(request.POST, instance=request.user)
# #             if form.is_valid():
# #                 form.save()
# #                 return redirect("profile_view")

# #         elif "update_picture" in request.POST:  # Updating profile picture
# #             picture_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
# #             if picture_form.is_valid():
# #                 picture_form.save()
# #                 return redirect("profile_view")

# #     else:
# #         form = UserUpdateForm(instance=request.user)
# #         picture_form = ProfileUpdateForm(instance=user_profile)

# #     return render(request, "profile_app/profile.html", {
# #         "form": form,
# #         "picture_form": picture_form,
# #         "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else "/static/default-profile.png",
# #     })

# # # @login_required
# # # def chat_view(request):
# # #     messages = Message.objects.filter(
# # #     sender=request.user
# # # ) | Message.objects.filter(
# # #     recipient=request.user
# # # ).order_by("timestamp")

# # #     users = User.objects.exclude(id=request.user.id)  # Get other users for dropdown
    
# # #     return render(request, "chat.html", {"messages": messages, "users": users})



# # @login_required
# # def logout_view(request):
# #     logout(request)
# #     return redirect("frontpage")  # Redirect to home after logout



# # # def messages_view(request, receiver_id=None):
# # #     users = User.objects.exclude(id=request.user.id)  # Exclude current user
# # #     selected_user = None

# # #     if receiver_id:
# # #         selected_user = get_object_or_404(User, id=receiver_id)

# # #     return render(request, "profile_app/messages.html", {
# # #         "users": users,
# # #         "selected_user": selected_user,
# # #         "messages": Message.objects.filter(
# # #             Q(sender=request.user, receiver=selected_user) |
# # #             Q(sender=selected_user, receiver=request.user)
# # #         ).order_by("timestamp") if selected_user else []
# # #     })
# # def messages_view(request):
# #     users = User.objects.exclude(id=request.user.id)  # Exclude self
# #     selected_user = None
# #     messages = []

# #     if request.method == "POST" and "receiver" in request.POST:
# #         selected_user = User.objects.get(id=request.POST["receiver"])
# #         messages = Message.objects.filter(
# #             sender__in=[request.user, selected_user],
# #             receiver__in=[request.user, selected_user]
# #         ).order_by("timestamp")

# #     print(f"Selected User: {selected_user}")  # Debugging
# #     print(f"Messages: {messages}")  # Debugging

# #     return render(request, "chat.html", {
# #         "users": users,
# #         "selected_user": selected_user,
# #         "messages": messages
# #     })

# # from django.shortcuts import get_object_or_404
# # from django.http import JsonResponse
# # from .models import Message

# # def send_message(request):
# #     if request.method == "POST":
# #         sender = request.user
# #         receiver_id = request.POST.get("receiver")  # Expecting ID instead of username
# #         message_content = request.POST.get("message")

# #         receiver = get_object_or_404(User, id=receiver_id)  # Use ID instead

# #         # Encrypt message before saving
# #         message = Message(sender=sender, receiver=receiver)
# #         message.encrypt_message(message_content)
# #         message.save()

# #         return JsonResponse({"status": "Message sent and encrypted!"})

# # from django.shortcuts import get_object_or_404, render
# # from .models import Message

# # def chat_view(request, receiver_username):
# #     receiver = get_object_or_404(User, username=receiver_username)
# #     messages = Message.objects.filter(
# #         sender=request.user, receiver=receiver
# #     ) | Message.objects.filter(
# #         sender=receiver, receiver=request.user
# #     )
# #     messages = messages.order_by("timestamp")

# #     return render(request, "profile_app/chat.html", {"messages": messages, "receiver": receiver})

# # # def chat_view(request, receiver_username):
# # #     receiver = get_object_or_404(User, username=receiver_username)
# # #     messages = Message.objects.filter(sender=request.user, receiver=receiver) | \
# # #                Message.objects.filter(sender=receiver, receiver=request.user)

# # #     message_list = [
# # #         {"sender": msg.sender.username, "message": msg.decrypt_message(), "timestamp": msg.timestamp}
# # #         for msg in messages
# # #     ]

# # #     return JsonResponse({"messages": message_list})
