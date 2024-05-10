from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, DetailView, View
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe

from .models import GuestEmail, EmailActivation
from .forms import LoginForm, RegisterForm, GuestForm, EmailReactivationForm
from ecommerce.mixins import NextUrlMixin, RequestFormAttachMixin

# Create your views here.
class AccountsHomeView(LoginRequiredMixin, DetailView):
    template_name = 'auth/home.html'
    def get_object(self):
        return self.request.user
    
class AccountConfirmView(FormMixin, View):
    success_url= "/account/login"
    form_class = EmailReactivationForm
    key = None
    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, "Your email is confirmed. Please login.")
                return redirect('/account/login')
            else:
                activated_qs = qs.filter(is_activated=True)
                if activated_qs.exists():
                    reset_link = reverse("accounts:password_reset")
                    msg = f"""Your email has already been confirmed.
                    Do you need to <a href="{reset_link}">reset your password?</a>"""
                    messages.success(request, mark_safe(msg))
                    return redirect('/account/login')
        # if activated
        # redirect
        # if already activated
        # redirect
        context = {"form": self.get_form, "key": key }
        return render(request, 'registration/email/verification-error.html', context)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        msg = f"""Activation link sent, please check your email."""
        request = self.request
        email = form.cleaned_data.get("email")
        messages.success(request, msg)
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation_email()
        return super(AccountConfirmView, self).form_valid(form)
    
    def form_invalid(self, form):
        context = {'form': form, "key": self.key }
        return render(self.request, 'registration/email/verification-error.html', context)



# def guest_register_view(request):
#     form = GuestForm(request.POST or None)
#     context = {
#         "form": form,
#     }
#     next_ = request.GET.get("next")
#     next_post = request.POST.get("next")
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         email = form.cleaned_data.get("email")
#         new_guest_email = GuestEmail.objects.create(email=email)
#         request.session["guest_email_id"] = new_guest_email.id
#         if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
#             return redirect(redirect_path)
#         else:
#             return redirect("account:register")
#     return redirect("account:register")

class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = "/account/register"

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)
    
    # def form_valid(self, form):
    #     request = self.request
    #     email = form.cleaned_data.get("email")
    #     new_guest_email = GuestEmail.objects.create(email=email)
    #     return redirect(self.get_next_url())



class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'auth/login.html'
    default_next = '/'

    def form_valid(self, form):
            next_path = self.get_next_url()
            return redirect(next_path)

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
    success_url = '/account/login'

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