# Create your views here.

from dependency_injector.wiring import inject, Provide
from django.http import HttpRequest, Http404
from django.shortcuts import render
from marshmallow import ValidationError

from core.services import ITradingService, ITransactionService, IAccountService
from stock_trading.forms import BuyStockForm, SellStockForm


@inject
def stock_market(
    request: HttpRequest,
    account_id,
    trading_service: ITradingService = Provide["trading_service"],
    account_service: IAccountService = Provide["account_service"],
):
    try:
        # Fetch account details
        account = account_service.get_account(account_id)
        if not account:
            raise ValidationError("No account found.")

        # Fetch available stocks
        available_stocks = trading_service.get_all_available_stocks()
        if not available_stocks:
            raise ValidationError("No available stocks.")

        # Fetch user stocks portfolio
        portfolio = trading_service.get_all_user_stocks(account_id)
        message = "No stocks are currently owned. Discover available stocks in the Discover Tab!" if not portfolio else ""

        # Render the dashboard
        return render(
            request,
            "stock_trading/dashboard.html",
            {
                "account_id": str(account_id),
                "available_funds": account_service.get_balance(account.reference_account_id),
                "portfolio": portfolio,
                "total_portfolio_value": trading_service.get_portfolio_value(account_id),
                "available_stocks": available_stocks,
                "message": message,
            },
        )
    except ValidationError as e:
        # Handle unexpected validation errors
        return render(
            request,
            "stock_trading/dashboard.html",
            {
                "account_id": str(account_id),
                "available_funds": 0,
                "portfolio": [],
                "total_portfolio_value": 0,
                "available_stocks": [],
                "message": f"An error occurred: {str(e)}",
            },
        )

@inject
def buy_stock(
    request,
    account_id,
    stock_id,
    trading_service: ITradingService = Provide["trading_service"],
    account_service: IAccountService = Provide["account_service"]
):
    stock = trading_service.get_stock(stock_id)
    if request.method == "POST":
        form = BuyStockForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            try:
                # Process the stock purchase
                trading_service.buy_stock(account_id, stock_id, quantity)

                # Render success screen
                return render(request, "stock_trading/success_screen.html", {
                    "success": True,
                    "message": "Stock purchased successfully!",
                    "account_id": account_id,
                })
            except ValidationError as e:
                # Check if the error is related to overdraft
                if "Overdraft limit" in str(e):
                    error_message = f"Purchase failed: {str(e)}"
                else:
                    error_message = "An error occurred: " + str(e)

                # Render failure screen
                return render(request, "stock_trading/success_screen.html", {
                    "success": False,
                    "message": error_message,
                    "account_id": account_id,
                })

    else:
        form = BuyStockForm()

    return render(request, "stock_trading/buy_stock.html", {"form": form, "account_id": account_id, "stock": stock})


@inject
def sell_stock(
    request,
    account_id,
    stock_id,
    trading_service: ITradingService = Provide["trading_service"]
):
    stock = trading_service.get_stock(stock_id)
    quantity_owned = trading_service.get_user_owned_stock(account_id, stock_id).quantity
    if request.method == "POST":
        form = SellStockForm(request.POST)
        if form.is_valid():
            quantity_to_sell = form.cleaned_data["quantity"]
            try:
                # Process the stock purchase
                trading_service.sell_stock(account_id, stock_id, quantity_to_sell)

                # Render success screen
                return render(request, "stock_trading/success_screen.html", {
                    "success": True,
                    "message": "Stock sold successfully!",
                    "account_id": account_id,
                })
            except ValidationError as e:
                # Check if the error is related to overdraft
                if "Overdraft limit" in str(e):
                    error_message = f"Sell failed: {str(e)}"
                else:
                    error_message = "An error occurred: " + str(e)

                # Render failure screen
                return render(request, "stock_trading/success_screen.html", {
                    "success": False,
                    "message": error_message,
                    "account_id": account_id,
                })

    else:
        form = SellStockForm()

    return render(request, "stock_trading/sell_stock.html", {"form": form, "account_id": account_id, "stock": stock, "quantity_owned": quantity_owned})
@inject
def history(
    request: HttpRequest,
    account_id,
    trading_service: ITradingService = Provide["trading_service"],
    transaction_service: ITransactionService = Provide["transaction_service"],
    account_service: IAccountService = Provide["account_service"],
):
    timeframe = request.GET.get("timeframe", "all_time")

    # Fetch the account object
    custody_account = account_service.get_account(account_id)
    if not custody_account:
        raise Http404("Account not found.")

    # Fetch stock transaction history
    stock_transaction_history = transaction_service.get_stock_transaction_history(custody_account.reference_account_id, timeframe)

    for transaction in stock_transaction_history:
        transaction["stock_symbol"] = trading_service.get_stock(transaction["stock_id"]).symbol
    # Prepare context for rendering

    context = {
        "account": custody_account,
        "stock_transaction_history": stock_transaction_history,
        "selected_timeframe": timeframe,
    }

    return render(request, "stock_trading/stock_transaction_history.html", context)
