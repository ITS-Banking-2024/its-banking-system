from unittest.mock import patch, MagicMock, Mock
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase, RequestFactory
from marshmallow.exceptions import ValidationError
from django.http import Http404
from uuid import uuid4
from decimal import Decimal
from stock_trading.views import history

from core.services import ITradingService, IAccountService
from core.models import Account
from stock_trading.models import StockOwnership, Stock
from stock_trading.views import stock_market

class TestContainer(containers.DeclarativeContainer):
    trading_service = providers.Singleton(
        MagicMock,
        spec=ITradingService
    )

    stock_ownership_factory = providers.Factory(
        MagicMock,
        spec=StockOwnership
    )

    account_factory = providers.Factory(
        MagicMock,
        spec=Account
    )

    account_service = providers.Singleton(
        MagicMock,
        spec=IAccountService
    )

    stock_factory = providers.Factory(
        MagicMock,
        spec=Stock
    )


class StockTradingViewsTest(TestCase):

    def setUp(self):
        self.container = TestContainer()

        self.account_service = self.container.account_service()
        self.trading_service = self.container.trading_service()
        self.account_factory = self.container.account_factory()
        self.stock_factory = self.container.stock_factory()
        self.stock_ownership_factory = self.container.stock_ownership_factory()  # Fixed typo

        self.stock_id = uuid4()
        self.account_id = uuid4()

        # Mock account
        self.valid_account = self.account_factory(
            account_id=self.account_id,
            reference_account_id=uuid4(),
            opening_balance=Decimal('1000.00')
        )


        # Mock stock and ownership
        self.mock_stock = self.stock_factory(
            id=self.stock_id,
            symbol="AAPL",
            stock_name="Apple Inc.",
            current_price=Decimal("150.00"),
        )

        self.user_portfolio_stock = self.stock_factory(
            id=self.stock_id,
            symbol="AAPL",
            stock_name="Apple Inc.",
            current_price=Decimal("150.00"),
            quantity=10
        )

        self.mock_ownership = self.stock_ownership_factory(
            stock=self.mock_stock,
            quantity=10
        )

        self.user_portfolio = [{
            "id": str(self.user_portfolio_stock.id),
            "name": self.user_portfolio_stock.stock_name,
            "symbol": self.user_portfolio_stock.symbol,
            "quantity": self.mock_ownership.quantity,
            "current_price": self.user_portfolio_stock.current_price,
            "total_value": round(self.mock_ownership.quantity * self.user_portfolio_stock.current_price, 2),
        }]

        self.container.wire(modules=["stock_trading.views"])

        # Set up request factory
        self.factory = RequestFactory()


    def test_stock_market_no_account(self):
        self.account_service.get_account.return_value = None

        response = self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

        # Assert the response status code
        self.assertEqual(response.status_code, 200)

        # Assert the rendered error message
        self.assertEqual(response.context["message"], "An error occurred: No account found.")

        self.assertTemplateUsed(response, "stock_trading/dashboard.html")


    def test_stock_market_no_available_stocks(self):
        self.account_service.get_account.return_value = self.valid_account
        self.trading_service.get_all_available_stocks.return_value = None

        response = self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

        self.assertEqual(response.context["message"], "An error occurred: No available stocks.")

        self.assertTemplateUsed(response, "stock_trading/dashboard.html")


    def test_stock_market_no_portfolio(self):
        self.account_service.get_account.return_value = self.valid_account
        self.trading_service.get_all_available_stocks.return_value = [
            {
                "id": str(self.mock_stock.id),
                "symbol": self.mock_stock.symbol,
                "name": self.mock_stock.stock_name,
                "current_price": self.mock_stock.current_price,
                "number_available": self.mock_ownership.quantity,
            }
        ]
        self.trading_service.get_all_user_stocks.return_value = None

        response = self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

        self.assertEqual(response.context["message"], "No stocks are currently owned. Discover available stocks in the Discover Tab!")

    def test_stock_market_success(self):
        self.account_service.get_account.return_value = self.valid_account
        self.trading_service.get_all_available_stocks.return_value = [
            {
                "id": str(self.mock_stock.id),
                "symbol": self.mock_stock.symbol,
                "name": self.mock_stock.stock_name,
                "current_price": self.mock_stock.current_price,
                "number_available": self.mock_ownership.quantity,
            }
        ]
        self.trading_service.get_all_user_stocks.return_value = self.user_portfolio
        self.account_service.get_balance.return_value = Decimal("1000.00")  # Mock expected value

        # Use the Django test client to call the URL
        response = self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

        # Verify response status code
        self.assertEqual(response.status_code, 200)

        # Verify template used
        self.assertTemplateUsed(response, "stock_trading/dashboard.html")

        # Verify context data
        self.assertIn("account_id", response.context)
        self.assertEqual(response.context["account_id"], str(self.account_id))
        self.assertEqual(response.context["available_funds"], Decimal("1000.00"))
        self.assertEqual(response.context["portfolio"], self.user_portfolio)
        self.assertEqual(
            response.context["total_portfolio_value"],
            self.trading_service.get_portfolio_value.return_value
        )
        self.assertEqual(response.context["available_stocks"][0]["name"], self.mock_stock.stock_name)

    def test_buy_stock_get_request(self):
        response = self.client.get(reverse("stock_trading:buy_stock", args=[self.account_id, self.stock_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock_trading/buy_stock.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["account_id"], self.account_id)

    def test_buy_stock_post_invalid_form(self):
        form_data = {"stock": "", "quantity": "invalid"}

        with patch("stock_trading.views.BuyStockForm.is_valid", return_value=False):
            response = self.client.post(reverse("stock_trading:buy_stock", args=[self.account_id, self.stock_id]), data=form_data)
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
    def test_buy_stocks_with_valid_form(self, mock_buy_stock_form, mock_stock_get, mock_fetch_stock_price, mock_account_filter, mock_get_or_create):

        mock_trading_service = self.trading_service

        # Mock the stock object
        mock_stock = self.mock_stock
        mock_stock_get.return_value = mock_stock

        # Mock the stock price
        mock_fetch_stock_price.return_value = Decimal("150.00")

        # Mock account
        mock_account = self.valid_account
        mock_account_filter.return_value.first.return_value = mock_account

        # Mock stock ownership
        mock_ownership = self.mock_ownership
        mock_get_or_create.return_value = (mock_ownership, True)

        # Mock form behavior
        mock_form_instance = MagicMock()
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            "stock": mock_stock,
            "quantity": 5,
        }
        mock_buy_stock_form.return_value = mock_form_instance

        # POST request
        response = self.client.post(
            reverse("stock_trading:buy_stock", args=[self.account_id, self.stock_id]),
            data={"stock": str(mock_stock.id), "quantity": 5},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock_trading/success_screen.html")
        mock_trading_service.buy_stock.assert_called_once_with(self.account_id, self.stock_id, 5)

    def test_buy_stock_validation_error(self):
        pass # i don't know how to test this i tried many different options but it didn't work

    def test_sell_stock_get_request(self):
        response = self.client.get(reverse("stock_trading:sell_stock", args=[self.account_id, self.stock_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock_trading/sell_stock.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["account_id"], self.account_id)

    def test_sell_stock_post_invalid_form(self):
        form_data = {"stock": "", "quantity": "invalid"}

        with patch("stock_trading.views.SellStockForm.is_valid", return_value=False):
            response = self.client.post(reverse("stock_trading:sell_stock", args=[self.account_id, self.stock_id]), data=form_data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "stock_trading/sell_stock.html")
            self.assertIn("form", response.context)
            self.assertFalse(response.context["form"].is_valid())
            self.container.trading_service().sell_stock.assert_not_called()

    @patch("stock_trading.models.StockOwnership.objects.get")
    @patch("accounts.models.CheckingAccount.objects.filter")
    @patch("stock_trading.services.fetch_stock_price")
    @patch("stock_trading.models.Stock.objects.get")
    @patch("stock_trading.views.SellStockForm")
    def test_sell_stock_valid_form(self, mock_sell_stock_form, mock_stock_get, mock_fetch_stock_price, mock_account_filter, mock_get):

        mock_trading_service = self.trading_service

        # Mock the stock object
        mock_stock = self.mock_stock
        mock_stock_get.return_value = mock_stock

        # Mock the stock price
        mock_fetch_stock_price.return_value = Decimal("150.00")

        # Mock account
        mock_account = self.valid_account
        mock_account_filter.return_value.first.return_value = mock_account

        # Mock stock ownership
        mock_ownership = self.mock_ownership
        mock_get.return_value = mock_ownership

        # Mock form behavior
        mock_form_instance = MagicMock()
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            "stock": mock_stock,
            "quantity": 5,
        }
        mock_sell_stock_form.return_value = mock_form_instance

        # POST request
        response = self.client.post(
            reverse("stock_trading:sell_stock", args=[self.account_id, self.stock_id]),
            data={"stock": str(mock_stock.id), "quantity": 5},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock_trading/success_screen.html")
        mock_trading_service.sell_stock.assert_called_once_with(self.account_id, self.stock_id, 5)

    def test_sell_stock_validation_error(self):
        pass # the same as with buy stock validation error -> i have difficulties with accesing it and testing it

    def test_history_account_not_found(self):
        self.account_service.get_account.return_value = None

        response = self.client.get(reverse("stock_trading:history", args=[self.account_id]))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context["exception"], "Account not found.")

    @patch("core.services.ITradingService")
    @patch("core.services.ITransactionService")
    @patch("core.services.IAccountService")
    def test_history_view_successful(self, mock_account_service, mock_transaction_service, mock_trading_service):

        # I didn't figure out the way to test it with to see the contex so i only managed to do this

        # Mock request
        request = RequestFactory().get("/history", {"timeframe": "30_days"})
        account_id = "123e4567-e89b-12d3-a456-426614174000"  # A valid UUID string

        # Mock account
        mock_account = Mock()
        mock_account.reference_account_id = 100
        mock_account.account_id = account_id  # Ensure it matches the URL pattern
        mock_account_service.get_account.return_value = mock_account

        # Mock stock transaction history
        mock_transaction_service.get_stock_transaction_history.return_value = [
            {"stock_id": 1, "amount": 100},
            {"stock_id": 2, "amount": 200},
        ]

        # Mock trading service stock symbols
        mock_stock_1 = Mock(symbol="AAPL")
        mock_stock_2 = Mock(symbol="GOOG")
        mock_trading_service.get_stock.side_effect = [mock_stock_1, mock_stock_2]

        # Call the view
        response = history(
            request,
            account_id,
            trading_service=mock_trading_service,
            transaction_service=mock_transaction_service,
            account_service=mock_account_service,
        )

        self.assertEqual(response.status_code, 200)