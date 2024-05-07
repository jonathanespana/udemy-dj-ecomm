from django.contrib import admin
from .models import GuestEmail, EmailActivation

# Register your models here.
class GuestEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = GuestEmail

class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = EmailActivation

admin.site.register(GuestEmail, GuestEmailAdmin)
admin.site.register(EmailActivation, EmailActivationAdmin)
