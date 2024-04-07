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
from django.urls import path, include

from . import views

# from products_app.views import (
#         ProductListView, 
#         product_list_view, 
#         ProductDetailView, 
#         ProductDetailSlugView,
#         product_detail_view,
#         ProductFeaturedListView,
#         ProductFeaturedDetailView,
#         ) 

urlpatterns = [
    path('', views.home_page, name="home"),
    path('about/', views.about_page, name="about"),
    path('contact/', views.contact_page, name="contact"),
    path('login/', views.login_page, name="login"),
    path('register/', views.register_page, name="register"),
    path('admin/', admin.site.urls),
    path('products/', include(("products_app.urls", "products"), namespace="products")),
    path('search/', include(("search_app.urls", "search"), namespace="search")),
    path('tags/', include(("tags_app.urls", "tags"), namespace="tags")),

    # path('featured/', ProductFeaturedListView.as_view()),
    # path('featured/<int:pk>/', ProductFeaturedDetailView.as_view()),
    # path('products/', ProductListView.as_view()),
    # path('products-fbv/', product_list_view),
    # #path('products/<int:pk>/', ProductDetailView.as_view()),
    # path('products/<slug:slug_name>/', ProductDetailSlugView.as_view()),
    # path('products-fbv/<int:pk>/', product_detail_view),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
