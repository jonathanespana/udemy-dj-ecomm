from django.shortcuts import render

from django.views.generic import ListView

from products_app.models import Product

# Create your views here.

class SearchProductListView(ListView):
    context_object_name = "product_list"
    template_name = "search/view.html"

    def get_queryset(self, *args,**kwargs):
        request = self.request
        method_dict = request.GET
        print(request.GET)
        query = method_dict.get("q", None)
        if query is not None:
            return Product.products.search(query)
        #return Product.objects.filter(name_iexact="tee") // case sensitive exact search
        return Product.objects.none()

def product_list_view(request):
    all_products = Product.objects.all()
    context = {"product_list": all_products}
    return render(request, "search/view.html", context)