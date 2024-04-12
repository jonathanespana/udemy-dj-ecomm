from django.shortcuts import render, redirect

from orders_app.models import Order
from products_app.models import Product
from billing_app.models import BillingProfile
from accounts_app.models import GuestEmail
from .models import Cart
from accounts_app.forms import LoginForm, GuestForm
from addresses_app.forms import AddressForm

# Create your views here.
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
        else:
            cart_obj.products.add(product_obj)
        request.session['cart_items'] = cart_obj.products.count()
    return redirect("cart:home")

def checkout_home(request):
    cart_obj, cart_created = Cart.cart_manager.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")
    # user = request.user
    # billing_profile = None
    login_form = LoginForm()
    guest_form = GuestForm()
    shipping_address_form = AddressForm()
    billing_address_form = AddressForm()
    billing_profile, billing_profile_created = BillingProfile.billing_profile_manager.new_or_get(request)
    # guest_email_id = request.session.get("guest_email_id")
    # if user.is_authenticated:
    #     billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(user=user, email=user.email)
    # elif guest_email_id is not None:
    #     guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
    #     billing_profile, billing_guest_profile_created = BillingProfile.objects.get_or_create(email=guest_email_obj.email)
    # else:
    #     pass
    if billing_profile is not None:
        order_obj, order_obj_created = Order.order_manager.new_or_get(billing_profile, cart_obj)
        # order_qs = Order.objects.filter(billing_profile=billing_profile, cart=cart_obj, active=True)
        # if order_qs.count() == 1:
        #     order_obj = order_qs.first()
        # else:
        #     order_obj = Order.objects.create(
        #         cart=cart_obj,
        #         billing_profile=billing_profile
        #     )
    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "shipping_address_form": shipping_address_form,
        "billing_address_form": billing_address_form,
    }
    return render(request, 'cart/checkout.html', context)
