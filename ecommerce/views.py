from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ContactForm, LoginForm, RegisterForm

def home_page(request):
    first_name = request.session.get("first_name", "Unknown")
    print(first_name)
    context = {
        "title": "Hello World!",
        "content": "The regular stuff",
    }
    if request.user.is_authenticated:
        context["premium_content"] = "This is premium"
    return render(request, 'home_page.html', context)

def about_page(request):
    context = {
        "title": "About Us!",
        "content": "The about us stuff",
    }
    return render(request, 'home_page.html', context)

def contact_page(request):
    contact_form = ContactForm(request.POST)
    context = {
        "title": "Contact Us!",
        "form": contact_form,
    }
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
    return render(request, 'contact/view.html', context)

# def login_page(request):
#     form = LoginForm(request.POST)
#     context = {
#         "form": form,
#     }
#     if form.is_valid():
#         username = form.cleaned_data.get("username")
#         password = form.cleaned_data.get("password")
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             # A backend authenticated the credentials
#             login(request, user)
#             context['form'] = LoginForm()
#             print("User logged in")
#             return redirect("/login")
#             ...
#         else:
#             # No backend authenticated the credentials
#             ...
#     return render(request, 'auth/login.html', context)

# def register_page(request):
#     User = get_user_model()
#     form = RegisterForm(request.POST)
#     if form.is_valid():
#         print(form.cleaned_data)
#         username = form.cleaned_data.get("username")
#         email = form.cleaned_data.get("email")
#         password = form.cleaned_data.get("password")
#         new_user = User.objects.create_user(username, email, password)
#         if new_user:
#             print(new_user)
#         return redirect("/register")
#     context = {
#         "title": "Register!",
#         "form": form,
#     }
#     return render(request, 'auth/register.html', context)

