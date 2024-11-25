from django.urls import path

from . import views

app_name = "stock_trading"

urlpatterns = [
    path("", views.stock_market, name="stock_market"),
]