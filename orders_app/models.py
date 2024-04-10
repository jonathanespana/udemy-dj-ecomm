import math
from django.db import models
from django.db.models.signals import pre_save, post_save

from cart_app.models import Cart
from ecommerce.utils import unique_order_id_generator

# Create your models here.
ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('returned', 'Returned'),
)

class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=120, default="created")
    #billing_profile = 
    #shipping_address = 
    #billing_address = 
    shipping_total = models.DecimalField(default=9.99, max_digits=20, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)

    def __str__(self):
        return self.order_id
    
    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([ cart_total, shipping_total ])
        formatted_total = format(new_total,'.2f')
        self.total = formatted_total
        self.save()
        return  new_total
    
def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

pre_save.connect(pre_save_create_order_id, sender=Order)

def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart_id = cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total, sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order, sender=Order)
