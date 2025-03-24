from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from .models import Message
from .forms import MessageForm
# Registration view
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # The password is securely hashed automatically
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Profile management view (requires user to be logged in)
@login_required
def profile(request):
    if request.method == 'POST':
        # Bind forms with submitted data and files (for profile picture)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message, UserKeys
from .forms import MessageForm

@login_required
def messaging_home(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'accounts/messaging_home.html', {'users': users})


# @login_required
# def chat_view(request, username):
#     receiver = User.objects.get(username=username)

#     # Ensure the receiver has an RSA key pair
#     receiver_keys, created = UserKeys.objects.get_or_create(user=receiver)
#     if created:
#         receiver_keys.public_key, receiver_keys.private_key = UserKeys.generate_keys()
#         receiver_keys.save()

#     messages = Message.objects.filter(
#         sender=request.user, receiver=receiver
#     ) | Message.objects.filter(
#         sender=receiver, receiver=request.user
#     )
#     messages = messages.order_by('timestamp')

#     if request.method == 'POST':
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.sender = request.user
#             message.receiver = receiver

#             # Ensure sender has RSA keys
#             sender_keys, created = UserKeys.objects.get_or_create(user=request.user)
#             if created:
#                 sender_keys.public_key, sender_keys.private_key = UserKeys.generate_keys()
#                 sender_keys.save()

#             message.save()
#             return redirect('chat', username=username)
#     else:
#         form = MessageForm()

#     return render(request, 'accounts/chat.html', {'receiver': receiver, 'messages': messages, 'form': form})

def custom_admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

def manage_users(request):
    users = User.objects.all()  # Get all users
    return render(request, 'accounts/manage_users.html', {'users': users})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def chat_view(request, username):
    receiver = User.objects.get(username=username)
    return render(request, 'accounts/chat.html', {"receiver": receiver})


def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/edit_user.html', {'user': user})
