from typing import Any
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from cart_app.models import Cart
from .models import Product

# Create your views here.
class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.ftd.get_featured()
    
class ProductFeaturedDetailView(DetailView):
    #queryset = Product.objects.all()
    template_name = "products/featured-detail.html"
    
    def get_queryset(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        found_product = Product.ftd.get_featured().filter(pk=pk)
        if found_product is None:
            raise Http404("No product matches.")
        return found_product

class ProductListView(ListView):
    context_object_name = "product_list"
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView,self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.cart_manager.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

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
        found_product = Product.products.get_by_id(pk)
        print(found_product)
        if found_product is None:
            raise Http404("No product matches.")

        return found_product
    
class ProductDetailSlugView(DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView,self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.cart_manager.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug_name")
        print(slug)
        #found_product = Product.products.get_by_slug(slug)
        try:
            found_product = Product.objects.get(slug_name=slug)
        except Product.DoesNotExist:
            raise Http404("Not found ...")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug_name=slug)
            found_product = qs.first()
        except:
            raise Http404("hmmmmm")
        return found_product



    #product_detail = get_object_or_404(Product, pk=pk)
    #try:
    #    product_detail = Product.objects.get(pk=pk)
    #except Product.DoesNotExist:
    #    print("No product matches query")
    #    raise Http404("No product matches the given search.")
def product_detail_view(request, pk):
    found_product = Product.products.get_by_id(pk)
    print(found_product)
    if found_product is None:
        raise Http404("No product matches.")
    context = {"product": found_product}
    return render(request, "products/detail.html", context)


