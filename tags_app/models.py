from django.db import models
from products_app.models import Product

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=120)
    slug_name = models.SlugField()
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.name