from django.shortcuts import render, redirect

from orders_app.models import Order
from products_app.models import Product
from billing_app.models import BillingProfile
from accounts_app.models import GuestEmail
from .models import Cart
from accounts_app.forms import LoginForm, GuestForm
from addresses_app.forms import AddressForm
from addresses_app.models import Address

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
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    shipping_address_id = request.session.get("shipping_address_id", None)
    billing_address_id = request.session.get("billing_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.billing_profile_manager.new_or_get(request)
    address_qs = None
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
    
    if request.method == "POST":
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            del request.session["cart_items"]
            del request.session["cart_id"]
            return redirect("/cart/success")
    
    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
    }
    return render(request, 'cart/checkout.html', context)
