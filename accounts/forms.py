from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom labels/placeholders for better UX
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a unique username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email address'})
        
        if 'password1' in self.fields:
            self.fields['password1'].label = "Password"
            self.fields['password1'].widget.attrs.update({'placeholder': 'Create a strong password'})
        if 'password2' in self.fields:
            self.fields['password2'].label = "Confirm Password"
            self.fields['password2'].widget.attrs.update({'placeholder': 'Repeat your password'})

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
