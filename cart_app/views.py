from django.shortcuts import render

from .models import Cart

# Create your views here.
def create_cart(request):
    cart_obj = Cart.objects.create(user=None)
    return cart_obj

def cart_home(request):
    cart_id = request.session.get("cart_id", None)
    # if cart_id is None:
    #     #print("create new cart")
    #     cart_obj = create_cart()
    #     request.session["cart_id"] = cart_obj.id
    #     #request.session["cart_id"] = 25
    # else:
    qs = Cart.objects.filter(id=cart_id)
    if qs.count() == 1:
        cart_obj = qs.first()
        if request.user.is_authenticated and cart_obj.user is None:
            cart_obj.user = request.user
            cart_obj.save()
            print("cart id exists")
        elif request.user.is_authenticated and cart_obj.user is request.user:
            cart_obj = cart_obj
            print("cart exists and is associated with customer")
    else:
        cart_obj = Cart.cart_manager.cart_create(user=request.user)
        request.session["cart_id"] = cart_obj.id
    #'session_key' request.session.session_key
    #'set_expiry' request.session.session_expiry(300) num in milliseconds 5minutes 
    # set a session variable example first name
    # request.session["first_name"] = "Jonny"
    print(dir(request.session))
    return render(request, "cart/home.html")
