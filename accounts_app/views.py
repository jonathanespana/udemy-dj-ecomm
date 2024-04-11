from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegisterForm

# Create your views here.
def login_page(request):
    form = LoginForm(request.POST)
    context = {
        "form": form,
    }
    next_ = request.GET.get("next")
    next_post = request.POST.get("next")
    redirect_path = next_ or next_post or None
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        else:
            # No backend authenticated the credentials
            print("error")
    return render(request, 'auth/login.html', context)

def logout_view(request):
    logout(request)
    return redirect("home")

def register_page(request):
    User = get_user_model()
    form = RegisterForm(request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        new_user = User.objects.create_user(username, email, password)
        if new_user:
            print(new_user)
        return redirect("/register")
    context = {
        "title": "Register!",
        "form": form,
    }
    return render(request, 'auth/register.html', context)