from typing import Any
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404

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

    #product_detail = get_object_or_404(Product, pk=pk)
def product_detail_view(request, pk):
    try:
        product_detail = Product.objects.get(pk=pk)
        context = {"product": product_detail}
    except Product.DoesNotExist:
        print("No product matches query")
        raise Http404("No product matches the given search.")
    return render(request, "products/detail.html", context)
