from django.urls import path
from . import views




urlpatterns = [
    path('dashboard/' , views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),       
    path('about/', views.about_view, name='about'),
    path('profile/', views.profile_view, name='profile'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('delete-account-confirm/<int:uid>/<str:token>/', views.delete_account_confirm_view, name='delete_account_confirm'),
    path('activate-registration/<str:temp_token>/', views.activate_registration, name='activate_registration'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('password-reset-confirm/<int:uid>/<str:token>/', views.reset_password_confirmation_view, name='password_reset_confirm'),
    path('forgot-user-name/', views.forgot_username_view, name='forgot_username'),
    path('reset_username_confirmation_view/<int:uid>/<str:token>/', views.reset_username_confirmation_view, name='reset_username_confirmation'),

]