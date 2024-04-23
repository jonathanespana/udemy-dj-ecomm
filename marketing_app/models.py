from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

from .utils import Mailchimp

# Create your models here.
class MarketingPref(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True)
    mailchimp_subscribed = models.BooleanField(null=True, blank=True)
    mailchimp_msg = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
    


def create_marketing_pref_reciever(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().subscribe(instance.user.email)
        print(status_code, response_data)

post_save.connect(create_marketing_pref_reciever, sender=MarketingPref)

def update_marketing_pref_reciever(sender, instance, *args, **kwargs):
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            status_code, response_data = Mailchimp().subscribe(instance.user.email)
        else:
            status_code, response_data = Mailchimp().unsubscribe(instance.user.email)
        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
            instance.mailchimp_msg = response_data
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.mailchimp_msg = response_data

pre_save.connect(update_marketing_pref_reciever, sender=MarketingPref)


def make_marketing_pref_reciever(sender, instance, created, *args, **kwargs):
    if created:
        MarketingPref.objects.get_or_create(user=instance)

post_save.connect(make_marketing_pref_reciever, sender=settings.AUTH_USER_MODEL)
