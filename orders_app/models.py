import math
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.conf import settings

from cart_app.models import Cart
from billing_app.models import BillingProfile
from addresses_app.models import Address
from products_app.models import Product
from ecommerce.utils import unique_order_id_generator

# Create your models here.
ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('returned', 'Returned'),
)

class OrderManagerQuerySet(models.query.QuerySet):
    def by_request(self, request):
        billing_profile, created = BillingProfile.billing_profile_manager.new_or_get(request)
        return self.filter(billing_profile = billing_profile)
    
    def active_order(self):
        return self.exclude(status='created')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)
    
    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
                billing_profile=billing_profile, 
                cart=cart_obj, 
                active=True,
                status = "created",
            )
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(
                cart=cart_obj,
                billing_profile=billing_profile
            )
            created = True
        return obj, created


class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, related_name="shipping_address", null=True, blank=True, on_delete=models.CASCADE)
    billing_address = models.ForeignKey(Address, related_name="billing_address", null=True, blank=True, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=120, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=120, default="created")
    active = models.BooleanField(default=True) 
    shipping_total = models.DecimalField(default=9.99, max_digits=20, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order_manager = OrderManager()
    objects = models.Manager()

    def __str__(self):
        return self.order_id
    
    class Meta:
        ordering = ["-created_at", "-updated_at"]
    
    def get_absolute_url(self):
        return reverse("orders:orders-detail", kwargs={"order_id":self.order_id})
    
    def get_status(self):
        if self.status == 'returned':
            return "Refunder Order"
        elif self.status == 'shipped':
            return "Shipped"
        else:
            return "Getting Ready to Ship"

    
    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([ cart_total, shipping_total ])
        formatted_total = format(new_total,'.2f')
        self.total = formatted_total
        self.save()
        return  new_total
    
    def check_done(self):
        shipping_address_required = not self.cart.is_digital
        shipping_done = False
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True

        billing_profile = self.billing_profile
        billing_address = self.billing_address
        total = self.total
        if billing_profile and shipping_done and billing_address and total > 0:
            return True
        return False
    
    def update_purchase(self):
        for p in self.cart.products.all():
            obj, created = ProductPurchase.objects.get_or_create(
                order_id=self.order_id,
                product = p,
                billing_profile = self.billing_profile
            )
        return ProductPurchase.objects.filter(order_id=self.order_id).count()

    
    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = "paid"
                self.save()
                self.update_purchase()
        return self.status
        

    
def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

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

class ProductPurchaseQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_refunded=False)
    
    def digital(self):
        return self.filter(product__is_digital=True)
    
    def by_request(self, request):
        billing_profile, created = BillingProfile.billing_profile_manager.new_or_get(request)
        return self.filter(billing_profile = billing_profile)

class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()
    
    def digital(self):
        return self.get_queryset().active().digital()
    
    def by_request(self, request):
        return self.get_queryset().by_request(request)
    
    def products_by_request(self, request):
        qs = self.by_request(request).digital()
        product_ids = [x.product.id for x in qs]
        products_qs = Product.objects.filter(id__in=product_ids)
        return products_qs


class ProductPurchase(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.name

