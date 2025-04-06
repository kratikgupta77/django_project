from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm


# @login_required
def home(request):
    return render(request, 'home.html')

# social_media/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import CustomUserCreationForm,CustomAuthenticationForm

from profile_app.models import BannedEmail
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            # Check if the email is banned
            if BannedEmail.objects.filter(email=email).exists():
                form.add_error('email', "This email address is banned.")
                return render(request, 'social_media/signup.html', {'form': form})
            
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email confirmed
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()

            # Generate token and uid for activation email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(
                reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
            )

            send_mail(
                'Activate Your Account',
                f'Click the link to activate your account: {activation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return render(request, 'social_media/verify_email_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'social_media/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Make sure userprofile exists
        from profile_app.models import UserProfile
        if not hasattr(user, 'userprofile'):
            UserProfile.objects.create(user=user)

        login(request, user)
        return redirect('frontpage')
    else:
        return render(request, 'social_media/activation_failed.html')



def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile_view')  
    else:
        form = CustomAuthenticationForm()
    return render(request, "social_media/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
