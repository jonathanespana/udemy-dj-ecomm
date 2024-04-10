from django.shortcuts import render, redirect

from orders_app.models import Order
from products_app.models import Product
from .models import Cart

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
    else:
        order_obj, new_order_obj = Order.objects.get_or_create(cart=cart_obj)
    return render(request, 'cart/checkout.html',{"object": order_obj})