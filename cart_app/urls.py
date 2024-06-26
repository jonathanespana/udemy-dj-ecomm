from django.urls import path

from . import views


urlpatterns = [
    path('', views.cart_home, name="home"),
    path('update/', views.cart_update, name="update"),
    path('checkout/', views.checkout_home, name="checkout"),
    path('checkout/success/', views.checkout_complete_view, name="success"),
]