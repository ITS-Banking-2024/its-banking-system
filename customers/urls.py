from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.customers_login, name="customers_login"),
    path("logout/", views.customers_logout, name="customers_logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
]