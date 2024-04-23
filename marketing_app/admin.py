from django.contrib import admin
from .models import MarketingPref

# Register your models here.

class MarketingPrefAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'subscribed', 'updated_at']
    readonly_fields = ['mailchimp_subscribed', 'updated_at', 'created_at']
    class Meta:
        model: MarketingPref
        fields = [
            'user',
            'subscribed', 
            'mailchimp_msg', 
            'mailchimp_subscribed', 
            'updated_at', 
            'created_at']

admin.site.register(MarketingPref, MarketingPrefAdmin)
