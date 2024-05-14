from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin

from analytics_app.mixins import ObjectViewedMixin
from cart_app.models import Cart
from .models import Product

# Create your views here.
class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.ftd.get_featured()
    
class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    #queryset = Product.objects.all()
    template_name = "products/featured-detail.html"
    
    def get_queryset(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        found_product = Product.ftd.get_featured().filter(pk=pk)
        if found_product is None:
            raise Http404("No product matches.")
        return found_product

class UserProductHistoryView(LoginRequiredMixin, ListView):
    context_object_name = "product_list"
    template_name = "products/history-list.html"
    # template_name = "products/list.html" #display products once

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView,self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.cart_manager.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

    def get_queryset(self, *args,**kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product, model_queryset=False) #set to True to display product once
        # viewed_ids = [x.object_id for x in views]
        # return Product.objects.filter(pk__in = viewed_ids)
        return views

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

class ProductDetailView(ObjectViewedMixin, DetailView):
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
    
class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView,self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.cart_manager.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get("slug_name")
        print(slug)
        #found_product = Product.products.get_by_slug(slug)
        try:
            instance = Product.objects.get(slug_name=slug)
        except Product.DoesNotExist:
            raise Http404("Not found ...")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug_name=slug)
            instance = qs.first()
        except:
            raise Http404("hmmmmm")
        #object_viewed_signal.send(sender=instance.__class__, instance=instance , request=request)
        return instance



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


