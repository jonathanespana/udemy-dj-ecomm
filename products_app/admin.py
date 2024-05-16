from django.contrib import admin

from .models import Product, ProductFile

# Register your models here.

class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug_name": ["name"]
    }
    inlines = [ProductFileInline]
    class Meta:
        Model = Product

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductFile)

