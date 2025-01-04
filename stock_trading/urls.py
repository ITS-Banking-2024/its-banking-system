from django.urls import path

from . import views

app_name = "stock_trading"

urlpatterns = [
    path("<uuid:account_id>", views.stock_market, name="stock_market"),
    path("<uuid:account_id>/buy/", views.buy_stock, name="buy_stock"),

]