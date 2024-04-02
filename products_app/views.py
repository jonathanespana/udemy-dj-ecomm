from typing import Any
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404

from .models import Product

# Create your views here.
class ProductListView(ListView):
    model = Product
    context_object_name = "product_list"
    template_name = "products/list.html"

def product_list_view(request):
    all_products = Product.objects.all()
    context = {"product_list": all_products}
    return render(request, "products/list.html", context)

class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        return context

def product_detail_view(request, pk):
    product_detail = get_object_or_404(Product, pk=pk)
    context = {"product": product_detail}
    return render(request, "products/detail.html", context)
