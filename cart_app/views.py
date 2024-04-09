from django.shortcuts import render, redirect

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

    #cart_id = request.session.get("cart_id", None)
    # if cart_id is None:
    #     #print("create new cart")
    #     cart_obj = create_cart()
    #     request.session["cart_id"] = cart_obj.id
    #     #request.session["cart_id"] = 25
    # else:
    # qs = Cart.objects.filter(id=cart_id)
    # if qs.count() == 1:
    #     cart_obj = qs.first()
    #     if request.user.is_authenticated and cart_obj.user is None:
    #         cart_obj.user = request.user
    #         cart_obj.save()
    #         print("cart id exists")
    # else:
    #     cart_obj = Cart.cart_manager.cart_create(user=request.user)
    #     request.session["cart_id"] = cart_obj.id
    #'session_key' request.session.session_key
    #'set_expiry' request.session.session_expiry(300) num in milliseconds 5minutes 
    # set a session variable example first name
    # request.session["first_name"] = "Jonny"
