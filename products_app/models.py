import os
import random
from django.db import models

# Create your models here.

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.split(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1, 390148425)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f'products/{new_filename}/{final_filename}'

class ProductManager(models.Manager):
    def get_by_id(self, pk):
        qs = self.get_queryset().filter(pk=pk)
        if qs.count() == 1:
            return qs.first()
        return None

class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    price= models.DecimalField(decimal_places=2, max_digits=10, default=39.99)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)

    objects = ProductManager()

    def __str__(self):
        return self.name
