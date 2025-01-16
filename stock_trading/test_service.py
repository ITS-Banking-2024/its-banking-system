import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal

from stock_trading.services import TradingService, fetch_stock_price
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

    def test_buy_stock_negative_quantity(self):
        with self.assertRaises(ValidationError) as context:
            self.trading_service.buy_stock(self.account_uuid, self.stock_one_uuid, -10)

        self.assertIn("Quantity must be greater than zero.", str(context.exception))

    def test_buy_stock_account_not_found(self):
        # simulate random account id, so that the account is not found - using while to make sure we have different account id
        while True:
            random_account_id = uuid4()
            if random_account_id != self.account_uuid:
                break

        with self.assertRaises(ValidationError) as context:
            self.trading_service.buy_stock(
                account_id=random_account_id, stock_id=self.stock_one_uuid, quantity=10
            )
            # Assert the correct error message
            self.assertIn("Account not found.", str(context.exception))

    @patch("stock_trading.models.Stock.objects.get")
    def test_buy_stock_insufficient_funds(self, mock_get_stock):
        self.account.opening_balance = Decimal("100.00")

        mock_get_stock.return_value.current_price = Decimal("150.00")

        with self.assertRaises(ValidationError) as context:
            self.trading_service.buy_stock(self.account_uuid, self.stock_one_uuid, 10)

            self.assertIn("Insufficient funds to buy stock.", str(context.exception))



    @patch("stock_trading.models.StockOwnership.objects.get_or_create")
    @patch("stock_trading.models.Stock.objects.get")
    @patch("accounts.models.CheckingAccount.objects.filter")
    @patch("stock_trading.services.fetch_stock_price")
    def test_buy_stock_success(self, mock_fetch_stock_price, mock_account_filter, mock_get_stock, mock_get_or_create):
        # stock_price
        mock_fetch_stock_price.return_value = Decimal("150.00")

        # account
        mock_account_filter.return_value.first.return_value = self.account

        # stokc_details
        mock_get_stock.return_value = self.stock_one

        # ownership
        mock_get_or_create.return_value = (self.mock_ownership, True)

        result = self.trading_service.buy_stock(self.account_uuid, self.stock_one_uuid, 2)

        # assertions
        self.assertTrue(result)
        self.assertEqual(self.account.opening_balance, Decimal("700.00"))  # 1000 - (2 * 150)
        mock_fetch_stock_price.assert_called_once_with("AAPL")
        mock_account_filter.assert_called_once_with(account_id=self.account_uuid)
        mock_get_stock.assert_called_once_with(pk=self.stock_one_uuid)
        mock_get_or_create.assert_called_once_with(account=self.account, stock=self.stock_one)


    @patch("stock_trading.models.Stock.objects.get")
    @patch("accounts.models.CheckingAccount.objects.filter")
    @patch("stock_trading.services.fetch_stock_price")
    def test_buy_stock_failed(self, mock_fetch_stock_price, mock_account_filter, mock_get_stock):
        # price
        mock_fetch_stock_price.return_value = Decimal("150.00")

        # account
        mock_account_filter.return_value.first.return_value = self.account

        # stock details
        mock_get_stock.return_value = self.stock_one

        # simulate transaction failed to some reason
        with patch("stock_trading.models.StockOwnership.objects.get_or_create", side_effect=Exception("Unexpected error")):
            with self.assertRaises(ValidationError) as context:
                self.trading_service.buy_stock(self.account_uuid, self.stock_one_uuid, 2)

            self.assertIn("Stock purchase failed: Unexpected error", str(context.exception))

    def test_get_current_stock_price(self):

        result = self.trading_service.get_current_stock_price(self.mock_stock.symbol)

        current_price = fetch_stock_price(self.mock_stock.symbol)
        self.assertEqual(result, current_price)

    def test_get_current_stock_price_failed(self):
        not_existing_stock = "NOT_EXISTING_STOCK"
        with self.assertRaises(ValidationError) as context:
            self.trading_service.get_current_stock_price(not_existing_stock)

        self.assertIn(f"Failed to fetch stock price for {not_existing_stock}", str(context.exception))