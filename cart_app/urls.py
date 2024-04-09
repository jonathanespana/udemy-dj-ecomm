from django.urls import path

from . import views


urlpatterns = [
    path('', views.cart_home, name="home"),
    path('update/', views.cart_update, name="update"),
]