from django.http import JsonResponse, HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, redirect
from django.conf import settings

from .models import BillingProfile, Card

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY

# Create your views here.

def payment_method_view(request):
    # if request.user.is_authenticated:
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.my_customer_id
    #     print(billing_profile)

    billing_profile, billing_profile_created = BillingProfile.billing_profile_manager.new_or_get(request)
    if not billing_profile:
        return redirect('/cart')
    next_url = None
    next_ = request.GET.get('next') +'/'
    if url_has_allowed_host_and_scheme(next_, request.get_host()):
        next_url = next_
    return render(request, "billing/payment-method.html", {"publish_key": stripe_publishable_key, "next_url": next_url})

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def payment_method_create_view(request):
    if request.method == "POST" and is_ajax(request=request):
        billing_profile, billing_profile_created = BillingProfile.billing_profile_manager.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find user"}, status_code=401)
        
        token = request.POST.get("token")
        if token is not None:
            # customer = stripe.Customer.retrieve(billing_profile.customer_id)
            # card_response = customer.sources.create(source=token)
            # card_response = stripe.Customer.create_source(
            #     billing_profile.customer_id,
            #     source=token,
            # )
            # new_card_obj = Card.card_manager.add_new(billing_profile, card_response)
            new_card_obj = Card.card_manager.add_new(billing_profile, token)
            print(new_card_obj)
        return JsonResponse({"message": 'Success! Card added.'})
    return HttpResponse("error", status_code=401)