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
from django.urls import path

from . import views


urlpatterns = [
    #path('featured/', views.ProductFeaturedListView.as_view()),
    #path('featured/<int:pk>/', views.ProductFeaturedDetailView.as_view()),
    path('', views.ProductListView.as_view(), name="list"),
    #path('products-fbv/', views.product_list_view),
    #path('products/<int:pk>/', views.ProductDetailView.as_view()),
    path('<slug:slug_name>/', views.ProductDetailSlugView.as_view(), name="detail"),
    # path('<slug:slug_name>/<int:pk>/', views.ProductDownloadView.as_view(), name="download"),
    # path('products-fbv/<int:pk>/', views.product_detail_view),

]