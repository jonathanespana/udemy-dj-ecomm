from django.urls import path
from . import views


urlpatterns = [
    #path('login/', views.login_page, name="login"),
    path('', views.AccountsHomeView.as_view(), name="home"),
    path('details/', views.UserDetailUpdateView.as_view(), name="user-update"),
    path('email/confirm/<str:key>', views.AccountConfirmView.as_view(), name="email-confirm"),
    path('email/resend-confirmation', views.AccountConfirmView.as_view(), name="email-reconfirm"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.logout_view, name="logout"),
    #path('register/', views.register_page, name="register"),
    path('register/', views.RegisterView.as_view(), name="register"),
    # path('guest-register/', views.guest_register_view, name="guest_register"),
    path('guest-register/', views.GuestRegisterView.as_view(), name="guest_register"),
]