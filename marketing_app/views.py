from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, View
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

from .mixins import CsrfExemptMixin
from .forms import MarketingPrefForm
from .models import MarketingPref
from .utils import Mailchimp

mailchimp_audience_list_id = settings.MAILCHIMP_AUDIENCE_LIST_ID


# Create your views here.
class MarketingPrefUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPrefForm
    template_name = 'base/forms.html'
    success_url = '/settings/email'
    success_message = "Saved your new email preferences"

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return redirect('/accounts/login/?next=/settings/email')
        return super(MarketingPrefUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPrefUpdateView,self).get_context_data(*args, **kwargs)
        context['title'] = "Update Email Preferences"
        return context

    def get_object(self):
        user = self.request.user
        obj, created = MarketingPref.objects.get_or_create(user=user)
        return obj

class MailchimpWebhookView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(mailchimp_audience_list_id):
            hook_type = data.get('type')
            email = data.get('data[email]')
            response_status, response = Mailchimp().check_subscription_status(email)
            sub_status = response['status']
            is_subbed = None
            mailchimp_subbed = None
            if sub_status == 'subscribed':
                is_subbed, mailchimp_subbed = (True, True)
            elif sub_status == 'unsubscribed':
                is_subbed, mailchimp_subbed = (False, False)
            if is_subbed is not None and mailchimp_subbed is not None:
                qs = MarketingPref.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(subscribed=is_subbed, mailchimp_subscribed=mailchimp_subbed, mailchimp_msg=str(data))
        return HttpResponse("Thank you", status=200)


# def mailchimp_webhook_view(request):
#     data = request.POST
#     list_id = data.get('data[list_id]')
#     if str(list_id) == str(mailchimp_audience_list_id):
#         hook_type = data.get('type')
#         email = data.get('data[email]')
#         response_status, response = Mailchimp().check_subscription_status(email)
#         sub_status = response['status']
#         is_subbed = None
#         mailchimp_subbed = None
#         if sub_status == 'subscribed':
#             is_subbed, mailchimp_subbed = (True, True)
#         elif sub_status == 'unsubscribed':
#             is_subbed, mailchimp_subbed = (False, False)
#         if is_subbed is not None and mailchimp_subbed is not None:
#             qs = MarketingPref.objects.filter(user__email__iexact=email)
#             if qs.exists():
#                 qs.update(subscribed=is_subbed, mailchimp_subscribed=mailchimp_subbed, mailchimp_msg=str(data))
#     return HttpResponse("Thank you", status=200)