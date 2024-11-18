from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.customers_login, name="customers_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
]