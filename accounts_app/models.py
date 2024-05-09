from datetime import timedelta
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils import timezone
from django.urls import reverse


from ecommerce.utils import random_string_generator, unique_key_generator

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("You must add an email to create an account.")
        if not password:
            raise ValueError("You must enter a password to create an account.")

        user_obj = self.model(
            email=self.normalize_email(email),
            full_name = full_name,
        )

        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj
    
    def create_staffuser(self, email, full_name=None, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            full_name = full_name,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name=None, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            full_name = full_name,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(max_length=225, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email
    

class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        DEFAULT_ACTIVATION_DAYS
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range = now
        
        return self.filter(
            is_activated = False,
            forced_expired = False
        ).filter(
            created_at__gt = start_range,
            created_at__lte = end_range
        )
    

class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self.db)
    
    def confirmable(self):
        return self.get_queryset().confirmable()
    
    def email_exists(self, email):
        return self.get_queryset().filter(
            Q(email=email)
            ).filter(is_activated=False)


class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email
    
    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable() # 1 object
        if qs.exists():
            return True
        return False
    
    def activate(self):
        if self.can_activate():
            user = self.user
            user.is_active = True
            user.save()
            self.is_activated = True
            self.save()
            return True
        return False
    
    def regenerate_key(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False
    
    def send_activation_email(self):
        if not self.is_activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL')
                key_path = reverse("account:email-confirm", kwargs={'key':self.key})
                path = f'{base_url}{key_path}'
                context = {
                    'path': path,
                    'email': self.email,
                }
                txt_ = get_template("registration/email/verify.txt").render(context)
                html_ = get_template("registration/email/verify.html").render(context)
                subject = "1-Click Email Activation"
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [ self.email, ]
                sent_mail = send_mail(
                    subject,
                    txt_,
                    from_email,
                    recipient_list,
                    html_message=html_,
                    fail_silently=False,
                )
                return sent_mail
        return False
    
def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.is_activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation, sender=EmailActivation)

def post_save_user_create_reciever(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation_email()

post_save.connect(post_save_user_create_reciever, sender=User)

class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

