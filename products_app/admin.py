from django.contrib import admin

from .models import Product

# Register your models here.

class ProductSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug_name": ["name"]
    }

admin.site.register(Product, ProductSlugAdmin)

