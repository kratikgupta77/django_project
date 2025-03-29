from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
# @login_required
def home(request):
    return render(request, 'home.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()  
            login(request, user)  # Auto-login after signup
            return redirect('frontpage')  # Redirect after signup
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'social_media/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile_view')  # This must match name="profile"
    else:
        form = AuthenticationForm()
    return render(request, "social_media/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
