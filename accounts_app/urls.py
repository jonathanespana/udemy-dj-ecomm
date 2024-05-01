from django.urls import path
from . import views


urlpatterns = [
    #path('login/', views.login_page, name="login"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('home-fbv/', views.accounts_home_view, name="home-fbv"),
    path('home/', views.AccountsHomeView.as_view(), name="home"),
    path('logout/', views.logout_view, name="logout"),
    #path('register/', views.register_page, name="register"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('guest-register/', views.guest_register_view, name="guest_register"),
]