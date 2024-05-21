from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView, View
from django.http import Http404, JsonResponse
from django.shortcuts import render

from billing_app.models import BillingProfile
from .models import Order, ProductPurchase

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

class PurchaseLibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'
    def get_queryset(self):
        return ProductPurchase.objects.products_by_request(self.request)#.digital()
    

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

# class VerifyOwnership(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         if is_ajax(request=request):
#             data = request.GET
#             product_id = data.get('product_id')
#             if product_id is not None:
#                 product_id - int(product_id)
#                 ownership_ids = ProductPurchase.objects.products_by_id(request)
#                 if product_id in ownership_ids:
#                     return JsonResponse({'owner':True})
#             return JsonResponse({'owner':False})
#         raise Http404
        
