from django.shortcuts import render, redirect

# Create your views here.
from dependency_injector.wiring import inject, Provide
from django.http import HttpResponse, HttpRequest
from django.template import loader
from marshmallow import ValidationError

from accounts.models import AccountBase
from core.services import ITradingService
from stock_trading.forms import BuyStockForm
from stock_trading.models import StockOwnership
from django.apps import apps

# Create your views here.

@inject
def stock_market(request: HttpRequest, account_id, trading_service: ITradingService = Provide["trading_service"]):
    account = AccountBase.objects.filter(account_id=account_id).first()
    if not account:
        raise ValidationError("No account found.")

    available_stocks = trading_service.get_all_available_stocks()

    ownerships = StockOwnership.objects.filter(account=account)
    stocks = [
        {
            "name": ownership.stock.name,
            "symbol": ownership.stock.symbol,
            "quantity": ownership.quantity,
            "current_price": ownership.stock.get_current_stock_price(),
            "total_value": ownership.quantity * ownership.stock.get_current_stock_price(),
        }
        for ownership in ownerships
    ]
    total_value = sum(stock["total_value"] for stock in stocks)

    return render(request, "stock_trading/dashboard.html", {
        "account_id": account_id,
        "stocks": stocks,
        "total_value": total_value,
        "available_stocks": available_stocks
    })

def buy_stock(request, account_id, trading_service: ITradingService = Provide["trading_service"]):
    if request.method == "POST":
        form = BuyStockForm(request.POST)
        if form.is_valid():
            stock = form.cleaned_data["stock"]
            quantity = form.cleaned_data["quantity"]

            trading_service.buy_stock(account_id, stock_id=stock.id, quantity=quantity)

            return redirect("stock_trading:dashboard")

    else:
        form = BuyStockForm()

    return render(request, "stock_trading/buy_stock.html", {"form": form, "account_id": account_id,})
