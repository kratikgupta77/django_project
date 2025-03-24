from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from .models import Message
# Registration form extending UserCreationForm
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Optionally require an email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Form for updating username and email
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

# Form for updating the profile picture
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'encrypted_text']
        widgets = {
            'encrypted_text': forms.Textarea(attrs={'rows': 3}),
        }

