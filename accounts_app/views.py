from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, DetailView
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme

from .models import GuestEmail
from .forms import LoginForm, RegisterForm, GuestForm
from .signals import user_logged_in_signal

# Create your views here.
class AccountsHomeView(LoginRequiredMixin, DetailView):
    template_name = 'auth/home.html'
    def get_object(self):
        return self.request.user


def guest_register_view(request):
    form = GuestForm(request.POST or None)
    context = {
        "form": form,
    }
    next_ = request.GET.get("next")
    next_post = request.POST.get("next")
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get("email")
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session["guest_email_id"] = new_guest_email.id
        if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("accounts:register")
    return redirect("accounts:register")

class LoginView(FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'auth/login.html'

    def form_valid(self, form):
        request = self.request
        next_ = request.GET.get("next")
        next_post = request.POST.get("next")
        redirect_path = next_ or next_post or None
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            user_logged_in_signal.send(sender=user.__class__, instance=user, request=request)
            try:
                del request.session["guest_email_id"]
            except:
                pass
            if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        return super(LoginView, self).form_invalid(form)

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
            try:
                del request.session["guest_email_id"]
            except:
                pass
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

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth/register.html"
    success_url = '/accounts/login'

# def register_page(request):
#     User = get_user_model()
#     form = RegisterForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         return redirect("register")
#     context = {
#         "title": "Register!",
#         "form": form,
#     }
#     return render(request, 'auth/register.html', context)