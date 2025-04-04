from django import forms
from .models import Artifact

class ArtifactForm(forms.ModelForm):
    class Meta:
        model = Artifact
        fields = ['title', 'description', 'bidding_price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your item'}),
            'bidding_price': forms.NumberInput(attrs={'placeholder': 'Enter bidding price'}),
        }
