from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings

from orders_app.models import Order
from products_app.models import Product
from billing_app.models import BillingProfile
from accounts_app.models import GuestEmail
from .models import Cart
from accounts_app.forms import LoginForm, GuestForm
from addresses_app.forms import AddressForm
from addresses_app.models import Address

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
# Create your views here.


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.cart_manager.new_or_get(request)
    products = [{ 
        "name":x.name, 
        "price": x.price, 
        "url": x.get_absolute_url(), 
        "id": x.id, 
        } 
        for x in cart_obj.products.all()]
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj = Cart.cart_manager.new_or_get(request)
    return render(request, "cart/home.html", {"cart": cart_obj})

def cart_update(request):
    product_id = request.POST.get("product_id")
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user, product no longer available")
            return redirect("cart:home")
        cart_obj, new_obj = Cart.cart_manager.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session['cart_items'] = cart_obj.products.count()
        if is_ajax(request=request):
            print("Ajax request")
            json_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_obj.products.count(),
            }
            return JsonResponse(json_data, status=200)
            # return JsonResponse({"message": "Error 400"}, status_code=400)
    return redirect("cart:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.cart_manager.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    shipping_address_id = request.session.get("shipping_address_id", None)
    billing_address_id = request.session.get("billing_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.billing_profile_manager.new_or_get(request)
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.order_manager.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            order_obj.save()
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            order_obj.save()
            del request.session["billing_address_id"]
        has_card = billing_profile.has_card
    
    if request.method == "POST":
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, charge_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()
                del request.session["cart_items"]
                del request.session["cart_id"]
                return redirect("cart:success")
            else:
                print(charge_msg)
                return redirect("cart:checkout")
    
    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": stripe_publishable_key,
    }
    return render(request, 'cart/checkout.html', context)

def checkout_complete_view(request):
    return render(request, 'cart/checkout_success.html')
