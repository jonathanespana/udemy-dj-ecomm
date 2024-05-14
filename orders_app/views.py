from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import render

from billing_app.models import BillingProfile
from .models import Order

# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):
    template_name = "orders/order-list.html"
    
    def get_queryset(self):
        return Order.order_manager.by_request(self.request).active_order()


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "orders/order-detail.html"

    def get_object(self):
        # return Order.objects.get(id=self.kwargs.get("id"))
        # return Order.objects.get(=self.kwargs.get("id"))
        qs = Order.order_manager.by_request(self.request).filter(order_id = self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404
