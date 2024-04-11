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
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home_page, name="home"),
    path('about/', views.about_page, name="about"),
    path('contact/', views.contact_page, name="contact"),
    path('accounts/', include(("accounts_app.urls", "accounts"), namespace="accounts")),
    #path('logout/', LogoutView.as_view(), name="logout"),
    # path('register/', views.register_page, name="register"),
    path('admin/', admin.site.urls),
    path('products/', include(("products_app.urls", "products"), namespace="products")),
    path('cart/', include(("cart_app.urls", "cart"), namespace="cart")),
    path('search/', include(("search_app.urls", "search"), namespace="search")),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
