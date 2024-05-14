from django import forms
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import User, EmailActivation, GuestEmail
from .signals import user_logged_in_signal

class EmailReactivationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("account:register")
            msg = f"""Email not found, Do you like to <a href="{register_link}">register?</a>?"""
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email", "full_name"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField(label="Name", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    class Meta:
        model = User
        fields = ["full_name"]
    
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "full_name", "password", "is_active", "is_staff", "is_admin"]

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email", "full_name", "is_admin", "is_staff"]
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal Info", {"fields": ["full_name"]}),
        ("Permissions", {"fields": ["is_active", "is_admin", "is_staff"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email", "full_name"]
    ordering = ["email"]
    filter_horizontal = []

class GuestForm(forms.ModelForm):
    # email = forms.EmailField()
    class Meta:
        model = GuestEmail
        fields = ['email']

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(GuestForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session["guest_email_id"] = obj.id
        return obj


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")
        qs = User.objects.filter(email=email)
        # if email is registered
        if qs.exists():
            # check for active user
            not_active = qs.filter(is_active=False)
            if not_active.exists():
                # not active, check email activation
                link = reverse("account:email-reconfirm")
                reconfirm_msg = f"""<a href='{link}'>Resend Confirmation Email</a> """
                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    confirmable_msg = "Please check your email to confirm your account or " + reconfirm_msg.lower()
                    raise forms.ValidationError(mark_safe(confirmable_msg))
                email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
                if email_confirm_exists:
                    not_confirmed_msg = "Email not confirmed.  " + reconfirm_msg
                    raise forms.ValidationError(mark_safe(not_confirmed_msg))
                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError("Your profile is inactive")
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid Credentials")
        
        login(request, user)
        self.user = user
        user_logged_in_signal.send(sender=user.__class__, instance=user, request=request)
        try:
            del request.session["guest_email_id"]
        except:
            pass
        return data


    # def form_valid(self, form):
    #     request = self.request
    #     next_ = request.GET.get("next")
    #     next_post = request.POST.get("next")
    #     redirect_path = next_ or next_post or None
    #     email = form.cleaned_data.get("email")
    #     password = form.cleaned_data.get("password")
    #     user = authenticate(request, username=email, password=password)
    #     if user is not None:
    #         if not user.is_active:
    #             messages.errors(request, "This email is not currently active,  please confirm email and then try again")
    #             return super(LoginView, self).form_invalid(form)
    #         login(request, user)
    #         user_logged_in_signal.send(sender=user.__class__, instance=user, request=request)
    #         try:
    #             del request.session["guest_email_id"]
    #         except:
    #             pass
    #         if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect("/")
    #     return super(LoginView, self).form_invalid(form)

class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email", "full_name"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False # send verifcation or confirmation email via email
        if commit:
            user.save()
        return user

# class RegisterForm(forms.Form):
#     username = forms.CharField()
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput())
#     password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput())

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         username_query = User.objects.filter(username=username)
#         if username_query.exists():
#             raise forms.ValidationError("Username already taken")
#         return username


#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password')
#         password2 = cleaned_data.get('password2')
#         if password2 != password:
#             raise forms.ValidationError("Passwords must match, try again.")
#         return cleaned_data
    
# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)