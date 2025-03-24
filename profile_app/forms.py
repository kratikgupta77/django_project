from django import forms
from django.contrib.auth.models import User
from .models import UserProfile,Message
from django import forms
from .models import Message
from django.contrib.auth.forms import UserCreationForm
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  

    class Meta:
        model = UserProfile
        fields = ['user', 'email', 'password1', 'password2']

# Form for updating username and email
class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ['username']

# Form for updating the profile picture
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']



class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]  