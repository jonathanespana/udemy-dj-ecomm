"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path

from . import views
from products_app.views import ProductListView, product_list_view, ProductDetailView, product_detail_view

urlpatterns = [
    path('', views.home_page),
    path('about/', views.about_page),
    path('products/', ProductListView.as_view()),
    path('products-fbv/', product_list_view),
    path('product/<int:pk>/', ProductDetailView.as_view()),
    path('product-fbv/<int:pk>/', product_detail_view),
    path('contact/', views.contact_page),
    path('login/', views.login_page),
    path('register/', views.register_page),
    path('admin/', admin.site.urls),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
