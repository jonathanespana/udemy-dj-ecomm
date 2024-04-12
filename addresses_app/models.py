from django.db import models
from billing_app.models import BillingProfile

ADDRESS_TYPE_CHOICES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)

# Create your models here.
class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    address_type = models.CharField(choices=ADDRESS_TYPE_CHOICES, max_length=120)
    address_line1 = models.CharField(max_length=120)
    address_line2 = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    country = models.CharField(max_length=120, default="United States")
    postal_code = models.CharField(max_length=120)

    def __str__(self):
        return self.billing_profile.email



