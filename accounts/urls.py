from django.urls import path
from . import views

urlpatterns = [
    path("register_user/", views.register_user, name="register-user"),
    path("register_vendor/", views.register_vendor, name="register-vendor"),
]
