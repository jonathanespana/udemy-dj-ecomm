# accounts.passwords.urls.py 
from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

urlpatterns  = [
        path('password/change/', auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('accounts:password_change_done')), name='password_change'),
        path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
        path('password/reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'),
        path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
        path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]