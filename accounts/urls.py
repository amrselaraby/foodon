from django.urls import path
from . import views

urlpatterns = [
    path("register_user/", views.register_user, name="register-user"),
    path("register_vendor/", views.register_vendor, name="register-vendor"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("my_account/", views.my_account, name="my-account"),
    path("customer_dashboard/", views.customer_dashboard, name="customer-dashboard"),
    path("vendor_dashboard/", views.vendor_dashboard, name="vendor-dashboard"),
]
