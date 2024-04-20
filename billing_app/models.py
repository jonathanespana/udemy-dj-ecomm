from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from accounts_app.models import GuestEmail

User = settings.AUTH_USER_MODEL

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your models here.
class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get("guest_email_id")
        created = False
        obj = None
        if user.is_authenticated:
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
        else:
            pass
        return obj, created

class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    customer_id = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    objects = models.Manager()
    billing_profile_manager = BillingProfileManager()

    def __str__(self):
        return self.email
    
    def charge(self, order_obj, card=None):
        return Charge.charge_manager.card_charge(self, order_obj, card)
    
    def get_cards(self):
        return self.card_set.all()
    
    @property
    def has_card(self):
        instance = self
        card_qs = self.get_cards()
        return card_qs.exists()
    
    @property
    def default_card(self):
        default_cards = self.get_cards().filter(default=True)
        if default_cards.exists():
            return default_cards.first()
        return None
    
def billing_profile_created_reciever(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print('Sent API request to stripe')
        customer = stripe.Customer.create(
            email = instance.email
        )
        print(customer)
        instance.customer_id = customer.id

pre_save.connect(billing_profile_created_reciever, sender=BillingProfile)
    
def user_created_reciever(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_reciever, sender=User)


class CardManager(models.Manager):
    def add_new(self, billing_profile, token):
        if token:
            stripe_card_response = stripe.Customer.create_source(
                billing_profile.customer_id,
                source=token,
            )
            new_card = self.model(
                billing_profile = billing_profile,
                stripe_id = stripe_card_response.id,
                brand = stripe_card_response.brand,
                country = stripe_card_response.country,
                exp_month = stripe_card_response.exp_month,
                exp_year = stripe_card_response.exp_year,
                last4 = stripe_card_response.last4,
            )
            new_card.save()
            return new_card
        return None

class Card(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id =  models.CharField(max_length=120)
    brand = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    exp_month = models.IntegerField(blank=True, null=True)
    exp_year = models.IntegerField(blank=True, null=True)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    default = models.BooleanField(default=True)

    card_manager = CardManager()
    objects = models.Manager()

    def __str__(self):
        return f"{self.brand} {self.last4}"
    


class ChargeManager(models.Manager):
    def card_charge(self, billing_profile, order_obj, card=None):
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False, "No cards available"

        new_charge = stripe.Charge.create(
            amount = int(order_obj.total * 100),
            currency ="usd",
            customer = billing_profile.customer_id,
            source = card_obj.stripe_id,
            metadata = {
                "order_id": order_obj.order_id
            },
        )
        new_charge_obj = self.model(
            billing_profile = billing_profile,
            stripe_id = new_charge.id,
            paid = new_charge.paid,
            refunded = new_charge.refunded,
            outcome = new_charge.outcome,
            outcome_type = new_charge.outcome['type'],
            seller_message = new_charge.outcome.get('seller_message'),
            risk_level = new_charge.outcome.get('risk_level'),
        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message

class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id =  models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(blank=True, null=True)
    outcome_type = models.CharField(max_length=20, blank=True, null=True)
    seller_message = models.CharField(max_length=20, blank=True, null=True)
    risk_level = models.CharField(max_length=20, blank=True, null=True)

    charge_manager = ChargeManager()
    objects = models.Manager()