from django.contrib import admin

from .models import Tag

# Register your models here.
class TagSlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug_name": ["name"]
    }

admin.site.register(Tag, TagSlugAdmin)