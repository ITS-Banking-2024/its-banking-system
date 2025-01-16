from unittest.mock import patch, MagicMock
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase
from marshmallow.exceptions import ValidationError
from uuid import uuid4
from decimal import Decimal

from core.services import ITradingService
from stock_trading.models import StockOwnership, Stock


class TestContainer(containers.DeclarativeContainer):
    trading_service = providers.Singleton(
        MagicMock,
        spec=ITradingService
    )

    stock_ownership = providers.Factory(
        MagicMock,
        spec=StockOwnership
    )

    account_factory = providers.Factory(
        MagicMock,
        spec=StockOwnership
    )

    stock_factory = providers.Factory(
        MagicMock,
        spec=Stock
        )


class StockTradingViewsTest(TestCase):

    def setUp(self):
        self.container = TestContainer()
        self.stock_id = uuid4()
        self.account_id = uuid4()

        self.unvalid_account = MagicMock(first=MagicMock(return_value=None))

        # Mock an account
        self.valid_account = MagicMock(id=self.account_id)

        # Mock a stock and its ownership
        self.mock_stock = MagicMock(
            id=self.stock_id,
            symbol="AAPL",
            stock_name="Apple Inc.",
            current_price=150,
        )
        self.mock_ownership = MagicMock(
            stock=self.mock_stock,
            quantity=10
        )

        # Mock trading service stocks
        self.mock_available_stock = {
            "id": self.mock_stock.id,
            "symbol": self.mock_stock.symbol,
            "name": self.mock_stock.stock_name,
            "current_price": self.mock_stock.current_price,
            "number_available": self.mock_ownership.quantity,
        }


    def test_stock_market_view_no_account(self):

        with patch("stock_trading.views.AccountBase.objects.filter", return_value=self.unvalid_account):
            with self.assertRaises(ValidationError) as context:
                self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

            self.assertEqual(str(context.exception), "No account found.")

    @patch("stock_trading.views.StockOwnership.objects.filter")
    @patch("stock_trading.views.apps.get_model")
    @patch("stock_trading.views.AccountBase.objects.filter")
    @patch("stock_trading.views.Provide")
    def test_stock_market_view(self, mock_provide, mock_account_filter, mock_get_model, mock_ownership_filter):
        # Mock the account query
        mock_account_filter.return_value.first.return_value = self.valid_account

        # Mock the custody account and its stock ownerships
        mock_custody_account = MagicMock()
        mock_get_model.return_value.objects.first.return_value = mock_custody_account
        mock_ownership_filter.side_effect = lambda account: [self.mock_ownership] if account == mock_custody_account else []

        # Mock the trading service
        mock_provide.return_value["trading_service"].get_all_available_stocks.side_effect = lambda: [self.mock_available_stock]


        # Perform the GET request
        response = self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

        # Assertions
        self.assertEqual(response.status_code, 200)

        # Verify template used
        self.assertTemplateUsed(response, "stock_trading/dashboard.html")

        # Verify if context contains the data

        self.assertIn("account_id", response.context)
        self.assertIn("stocks", response.context)
        self.assertIn("total_value", response.context)
        self.assertIn("available_stocks", response.context)

        # get available stocks from response
        available_stocks = response.context.get('available_stocks', [])

        stock = available_stocks[0]
        self.assertEqual(stock['name'], "Apple Inc.")
        self.assertEqual(stock['current_price'], 150)
        self.assertEqual(stock['number_available'], 10)
        self.assertEqual(stock['symbol'], "AAPL")
        self.assertEqual(response.context["account_id"], self.account_id)


    # check if we can get acces to the vi
    def test_buy_stock_get_request(self):

        response = self.client.get(reverse("stock_trading:buy_stock", args=[self.account_id]))

        self.assertEqual(response.status_code, 200)


        self.assertTemplateUsed(response, "stock_trading/buy_stock.html")

        self.assertIn("form", response.context)
        self.assertEqual(response.context["account_id"], self.account_id)

    #chek if we put invalid acces we wil be redirected to the the same page with the form
    def test_buy_stock_post_invalid_form(self):
        form_data = {"stock": "", "quantity": "invalid"}


        with patch("stock_trading.views.BuyStockForm.is_valid", return_value=False):
            response = self.client.post(reverse("stock_trading:buy_stock", args=[self.account_id]), data=form_data)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "stock_trading/buy_stock.html")

            self.assertIn("form", response.context)
            self.assertFalse(response.context["form"].is_valid())


            self.container.trading_service().buy_stock.assert_not_called()


    @patch("stock_trading.models.StockOwnership.objects.get_or_create")
    @patch("accounts.models.CheckingAccount.objects.filter")
    @patch("stock_trading.services.fetch_stock_price")
    @patch("stock_trading.models.Stock.objects.get")
    @patch("stock_trading.views.BuyStockForm")
    @patch("stock_trading.views.Provide")
    def test_buy_stocks_with_valid_form(
        self, mock_provide, mock_buy_stock_form, mock_stock_get, mock_fetch_stock_price, mock_account_filter, mock_get_or_create
    ):

        # mock the trading service and its buy_stock method
        mock_trading_service = MagicMock()
        mock_trading_service.buy_stock.return_value = True
        mock_provide.return_value["trading_service"] = mock_trading_service

        # mock the stock object
        mock_stock = MagicMock()
        mock_stock.id = uuid4()
        mock_stock.stock_name = "Apple Inc."
        mock_stock_get.return_value = mock_stock

        # mock the stock price
        mock_fetch_stock_price.return_value = Decimal("150.00")

        # mock account
        mock_account = MagicMock()
        mock_account.id = uuid4()
        mock_account.opening_balance = Decimal("10000.00")
        mock_account_filter.return_value.first.return_value = mock_account

        # mock stock_ownership
        mock_ownership = MagicMock()
        mock_get_or_create.return_value = (mock_ownership, True)

        # mock behaviour
        mock_form_instance = MagicMock()
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            "stock": mock_stock,
            "quantity": 5,
        }
        mock_buy_stock_form.return_value = mock_form_instance

        # POST request
        response = self.client.post(
            reverse("stock_trading:buy_stock", args=[str(mock_account.id)]),
            data={"stock": str(mock_stock.id), "quantity": 5},
        )

        # assertions
        form_call_args = mock_buy_stock_form.call_args[0][0]
        self.assertEqual(form_call_args.get("stock"), str(mock_stock.id))
        self.assertEqual(form_call_args.get("quantity"), "5")

        mock_form_instance.is_valid.assert_called_once()
        mock_fetch_stock_price.assert_called_once_with("Apple Inc.")
        mock_account_filter.assert_called_once_with(account_id=mock_account.id)
        mock_get_or_create.assert_called_once_with(account=mock_account, stock=mock_stock)

        # assert if we are doing redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("stock_trading:dashboard"))