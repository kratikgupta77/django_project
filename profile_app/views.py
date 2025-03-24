from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm


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

    # Maintain selected receiver even after sending a message
    if request.method == "POST" and "receiver" in request.POST:
        request.session["selected_receiver"] = request.POST.get("receiver")

    receiver_id = request.session.get("selected_receiver")  
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
        text = request.POST.get("text")
        if receiver_id and text:
            receiver = get_object_or_404(User, id=receiver_id)
            Message.objects.create(sender=request.user, receiver=receiver, text=text)
            request.session["selected_receiver"] = receiver_id  # Keep receiver after sending message
            return redirect("messages_view")

    return redirect("messages_view")