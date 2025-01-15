import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal

from stock_trading.services import TradingService
from stock_trading.models import Stock, StockOwnership
from marshmallow import ValidationError
from core.models import Account

class TestStockTrading(unittest.TestCase):
    def setUp(self):
        self.trading_service = TradingService()

        # Mock UUIDs
        self.stock_one_uuid = uuid4()
        self.stock_two_uuid = uuid4()
        self.account_uuid = uuid4()

        # Mock account
        self.account = Mock(spec=Account)
        self.account.account_id = self.account_uuid
        self.account.opening_balance = Decimal("1000.00")

        # Mock stocks
        self.stock_one = Mock(spec=Stock)
        self.stock_one.id = self.stock_one_uuid
        self.stock_one.stock_name = "AAPL"

        self.stock_two = Mock(spec=Stock)
        self.stock_two.id = self.stock_two_uuid
        self.stock_two.stock_name = "GOOGL"

        # Mock stock ownership and available stocks
        self.mock_stock = MagicMock(
            id=self.stock_one_uuid,
            symbol="AAPL",
            stock_name="Apple Inc.",
            current_price=150,
        )

        self.mock_ownership = MagicMock(
            stock=self.mock_stock,
            quantity=10
        )

        self.mock_available_stock = {
            "id": self.mock_stock.id,
            "symbol": self.mock_stock.symbol,
            "name": self.mock_stock.stock_name,
            "current_price": self.mock_stock.current_price,
            "number_available": self.mock_ownership.quantity,
        }

    @patch("stock_trading.services.apps.get_model")
    def test_get_all_available_stocks_no_account(self, mock_get_model):
        mock_get_model.return_value.objects.first.return_value = None

        with self.assertRaises(ValidationError) as context:
            self.trading_service.get_all_available_stocks()

        self.assertIn("Bank custody account not found.", str(context.exception))

    @patch("stock_trading.models.StockOwnership.objects.filter")
    @patch("stock_trading.services.apps.get_model")
    def test_get_all_available_stocks_returns_stocks(self, mock_get_model, mock_ownership_filter):
        # Mock the custody account
        mock_get_model.return_value.objects.first.return_value = self.account

        # Mock stock ownerships
        mock_ownership_filter.return_value = [self.mock_ownership]

        # Call the method
        result = self.trading_service.get_all_available_stocks()

        # Check the result
        expected_result = [
            {
                "id": self.mock_stock.id,
                "symbol": self.mock_stock.symbol,
                "name": self.mock_stock.stock_name,
                "current_price": self.mock_stock.current_price,
                "number_available": self.mock_ownership.quantity,
            }
        ]
        self.assertEqual(result, expected_result)

    def test_get_all_available_stokc_failed_to_fetch_stocks(self):
        with patch("stock_trading.services.apps.get_model") as mock_get_model:
            mock_get_model.side_effect = Exception("Failed to fetch stocks")

            with self.assertRaises(ValidationError) as context:
                self.trading_service.get_all_available_stocks()

            self.assertIn("Failed to fetch available stocks: Failed to fetch stocks", str(context.exception))