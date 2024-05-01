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
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from . import views
from addresses_app.views import checkout_address_create_view, checkout_prev_address_use
from cart_app.views import cart_detail_api_view
from billing_app.views import payment_method_view, payment_method_create_view
from marketing_app.views import MarketingPrefUpdateView, MailchimpWebhookView

urlpatterns = [
    path('', views.home_page, name="home"),
    path('about/', views.about_page, name="about"),
    path('contact/', views.contact_page, name="contact"),
    path('checkout_address_create/', checkout_address_create_view, name="checkout_address_create"),
    path('checkout/payment-method/', payment_method_view, name="checkout_payment_method"),
    path('checkout/payment-create/', payment_method_create_view, name="checkout_payment_method_endpoint"),
    path('use_prev_address/', checkout_prev_address_use, name="use_prev_address"),
    path('cart/api/cart/', cart_detail_api_view, name="api_cart_refresh"),
    path('account/', include(("accounts_app.urls", "account"), namespace="account")),
    path('accounts/', RedirectView.as_view(url="/account")),
    path('settings/', RedirectView.as_view(url="/account")),
    path('products/', include(("products_app.urls", "products"), namespace="products")),
    path('cart/', include(("cart_app.urls", "cart"), namespace="cart")),
    path('search/', include(("search_app.urls", "search"), namespace="search")),
    path('settings/email/', MarketingPrefUpdateView.as_view() ,name="marketing-pref"),
    path('webhooks/mailchimp/', MailchimpWebhookView.as_view() ,name="mailchimp-webhook"),
    #path('logout/', LogoutView.as_view(), name="logout"),
    # path('register/', views.register_page, name="register"),
    path('admin/', admin.site.urls),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

