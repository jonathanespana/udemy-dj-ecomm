from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import AddressForm
from billing_app.models import BillingProfile

# Create your views here.
def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    context = {
        "form": form,
    }
    next_ = request.GET.get("next")
    next_post = request.POST.get("next")
    redirect_path = next_ or next_post or None
    if form.is_valid():
        print(request.POST)
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.billing_profile_manager.new_or_get(request)
        if billing_profile is not None:
            address_type = request.POST.get("address_type", "shipping")
            instance.billing_profile = billing_profile
            instance.address_type = request.POST.get("address_type", "shipping")
            instance.save()

            request.session[address_type + "_address_id"] = instance.id
        else:
            return redirect("cart:checkout")
        if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("cart:checkout")
    return redirect("cart:checkout")


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
#             return redirect("accounts:register")
#     return redirect("accounts:register")