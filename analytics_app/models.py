from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import pre_save, post_save

from accounts_app.signals import user_logged_in_signal
from .signals import object_viewed_signal
from .utils import get_client_id

# Create your models here.
User = settings.AUTH_USER_MODEL

FORCE_SESSION_TO_ONE = getattr(settings,'FORCE_SESSION_TO_ONE', False)
FORCE_INACTIVE_USER_ENDSESSION = getattr(settings,'FORCE_INACTIVE_USER_ENDSESSION', False)

class ObjectViewedQuerySet(models.query.QuerySet):
    def by_model(self, model_class, model_queryset=False):
        c_type = ContentType.objects.get_for_model(model_class)
        qs = self.filter(content_type=c_type)
        if model_queryset:
            viewed_ids = [x.object_id for x in qs]
            return model_class.objects.filter(pk__in=viewed_ids)
        return qs


class ObjectViewedManager(models.Manager):
    def get_queryset(self):
        return ObjectViewedQuerySet(self.model, using=self._db)
    
    def by_model(self, model_class, model_queryset=False):
        return self.get_queryset().by_model(model_class, model_queryset)

class ObjectViewed(models.Model):
    user =  models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=225, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    objects = ObjectViewedManager()

    def __str__(self):
        return f"{self.content_object} viewed on {self.updated_at}"
    
    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Object viewed"
        verbose_name_plural = "Objects viewed"

def object_viewed_reciever(sender, instance, request, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(sender)
    # print(instance)
    # print(request)
    print(request.user.id)
    if request.user.id is None:
        new_view_obj = ObjectViewed.objects.create(
            ip_address = get_client_id(request),
            content_type = c_type,
            object_id = instance.id,
        )
    else: 
        new_view_obj = ObjectViewed.objects.create(
            user = request.user,
            ip_address = get_client_id(request),
            content_type = c_type,
            object_id = instance.id,
        )

object_viewed_signal.connect(object_viewed_reciever)


class UserSession(models.Model):
    user =  models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=225, blank=True, null=True)
    session_key = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_ended = models.BooleanField(default=False)

    def end_session(self):
        session_key = self.session_key
        is_ended = self.is_ended
        try:
            Session.objects.get(pk=session_key).delete()
            self.is_active = False
            self.is_ended = True
            self.save()
        except:
            pass
        return self.is_ended
    
def post_save_session_reciver(sender, instance, created, *args, **kwargs):
    if created:
        qs = UserSession.objects.filter(user=instance.user).exclude(id=instance.id)
        for i in qs:
            i.end_session()
    if not instance.is_active and not instance.is_ended:
        instance.end_session()

if FORCE_SESSION_TO_ONE:
    post_save.connect(post_save_session_reciver, sender=UserSession)

def post_save_user_changed_reciever(sender, instance, created, *args, **kwargs):
    if not created:
        if instance.is_active == False:
            qs = UserSession.objects.filter(user=instance.user)
            for i in qs:
                i.end_session()

if FORCE_INACTIVE_USER_ENDSESSION:
    post_save.connect(post_save_user_changed_reciever, sender=User)


def user_logged_in_reciever(sender, instance, request, *args, **kwargs):
    user = instance
    ip_address = get_client_id(request)
    session_key = request.session.session_key
    UserSession.objects.create(
        user = user,
        ip_address = ip_address,
        session_key = session_key

    )

user_logged_in_signal.connect(user_logged_in_reciever)