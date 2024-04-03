from typing import Any
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Product

# Create your views here.
class ProductListView(ListView):
    context_object_name = "product_list"
    template_name = "products/list.html"

    def get_queryset(self, *args,**kwargs):
        request = self.request
        return Product.objects.all()

def product_list_view(request):
    all_products = Product.objects.all()
    context = {"product_list": all_products}
    return render(request, "products/list.html", context)

class ProductDetailView(DetailView):
    #queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        return context
    
    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get("pk")
        found_product = Product.objects.get_by_id(pk)
        print(found_product)
        if found_product is None:
            raise Http404("No product matches.")

        return found_product

    #product_detail = get_object_or_404(Product, pk=pk)
    #try:
    #    product_detail = Product.objects.get(pk=pk)
    #except Product.DoesNotExist:
    #    print("No product matches query")
    #    raise Http404("No product matches the given search.")
def product_detail_view(request, pk):

    found_product = Product.objects.get_by_id(pk)
    print(found_product)
    if found_product is None:
        raise Http404("No product matches.")
    context = {"product": found_product}
    return render(request, "products/detail.html", context)
