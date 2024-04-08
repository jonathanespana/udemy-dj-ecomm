from django.db import models
from django.conf import settings

from products_app.models import Product

User = settings.AUTH_USER_MODEL

# Create your models here.
class CartManager(models.Manager):
    def cart_create(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    cart_manager = CartManager()

    def __str__(self):
        return str(self.id)

