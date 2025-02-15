from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Book, User
import re
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Password must be at least 8 characters long, include uppercase, lowercase, and a number.",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
            raise ValidationError("Password must contain at least 8 characters, including an uppercase letter, a lowercase letter, and a number.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match!")

        return cleaned_data
    
class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["pdf", "title", "desc", "author", "year", "genre"]