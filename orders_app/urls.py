from django.urls import path

from . import views


urlpatterns = [
    #path('login/', views.login_page, name="login"),
    path('', views.OrderListView.as_view(), name="orders-list"),
    # path('endpoint/verify/ownership/', views.VerifyOwnership.as_view(), name="verify-ownership"),
    path('<str:order_id>/', views.OrderDetailView.as_view(), name="orders-detail"),
    
]