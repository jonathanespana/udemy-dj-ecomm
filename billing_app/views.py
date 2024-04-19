from django.http import JsonResponse, HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY

# Create your views here.

def payment_method_view(request):
    next_url = None
    next_ = request.GET.get('next')
    if url_has_allowed_host_and_scheme(next_, request.get_host()):
        next_url = next_
    return render(request, "billing/payment-method.html", {"publish_key": stripe_publishable_key, "next_url": next_url})

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def payment_method_create_view(request):
    if request.method == "POST" and is_ajax(request=request):
        print(request.POST)
        return JsonResponse({"message": 'Success! Card added.'})
    return HttpResponse("error", status_code=401)