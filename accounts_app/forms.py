from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()

class GuestForm(forms.Form):
    email = forms.EmailField()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput())

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username_query = User.objects.filter(username=username)
        if username_query.exists():
            raise forms.ValidationError("Username already taken")
        return username


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password2 != password:
            raise forms.ValidationError("Passwords must match, try again.")
        return cleaned_data