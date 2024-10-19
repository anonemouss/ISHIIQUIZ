from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Post, Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Enter your reason for reporting...', 'rows': 3}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    contact_number = forms.CharField(required=True, max_length=15)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'contact_number', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise ValidationError("Username is already taken.")

        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise ValidationError("Email is already in use.")

        return cleaned_data


