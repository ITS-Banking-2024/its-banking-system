from unittest.mock import patch, MagicMock
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase, RequestFactory
from marshmallow.exceptions import ValidationError
from uuid import uuid4
from decimal import Decimal

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

    def test_buy_sock(self):
        pass