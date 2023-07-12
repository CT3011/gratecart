from django.urls import path

from . import views

app_name='accounts'

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('', views.dashboard, name="dashboard"),
    path('forgatePassword/', views.forgatePassword, name="forgatePassword"),
    path('resetPassword/', views.resetPassword, name="resetPassword"),

    path('activate/<uidb64>/<token>/', views.accounts, name='activate'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),

    path('my_orders/', views.my_orders, name="my_orders"),
    path('adit_profile/', views.adit_profile, name="adit_profile"),
    path('change_password/', views.change_password, name="change_password"),
    path('order_detailed/<int:order_id>/', views.order_detailed, name="order_detailed")
]
