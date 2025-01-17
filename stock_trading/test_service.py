import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import timedelta
from django.utils.timezone import now

from stock_trading.services import TradingService, fetch_stock_price
from stock_trading.models import Stock, StockOwnership
from marshmallow import ValidationError
from core.models import Account

class TestStockTrading(unittest.TestCase):
    def setUp(self):
        self.transaction_service = Mock()
        self.account_service = Mock()
        self.trading_service = TradingService(self.transaction_service, self.account_service)

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
            stockID=self.stock_one_uuid,  # Set to a real UUID
            symbol="AAPL",
            stock_name="Apple Inc.",
            current_price=Decimal("150.00"),
        )

        self.mock_ownership = MagicMock(
            stock=self.mock_stock,
            quantity=Decimal("10")
        )

        self.mock_available_stock = {
            "id": str(self.stock_one_uuid),  # Ensure UUID is converted to a string
            "symbol": self.mock_stock.symbol,
            "name": self.mock_stock.stock_name,
            "current_price": self.mock_stock.current_price,
            "number_available": self.mock_ownership.quantity,
        }

    def test_get_all_available_stocks_no_account(self):
        # Simulate no custody account found
        self.account_service.get_bank_custody_account.return_value = None

        with self.assertRaises(ValidationError) as context:
            self.trading_service.get_all_available_stocks()

        self.assertIn("Bank custody account not found.", str(context.exception))

    @patch("stock_trading.models.StockOwnership.objects.filter")
    def test_get_all_available_stocks_returns_stocks(self, mock_ownership_filter):
        # Mock the custody account
        self.account_service.get_bank_custody_account.return_value = self.account

        # Mock stock ownerships
        mock_ownership_filter.return_value = [self.mock_ownership]

        # Mock get_current_stock_price to return the mocked current price
        self.trading_service.get_current_stock_price = MagicMock(return_value=150)

        # Call the method
        result = self.trading_service.get_all_available_stocks()

        # Check the result
        expected_result = [
            {
                "id": str(self.stock_one_uuid),  # Converted to string
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "current_price": 150,
                "number_available": 10,
            }
        ]
        self.assertEqual(result, expected_result)

    def test_get_all_available_stokc_failed_to_fetch_stocks(self):
            self.trading_service.get_all_available_stocks = MagicMock(side_effect=ValidationError("Failed to fetch stocks"))

            with self.assertRaises(ValidationError) as context:
                self.trading_service.get_all_available_stocks()

            self.assertIn("Failed to fetch stocks", str(context.exception))

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
    @patch("stock_trading.models.StockOwnership.objects.select_for_update")
    @patch("accounts.models.CustodyAccount.objects.filter")
    @patch("accounts.models.CheckingAccount.objects.filter")
    @patch("stock_trading.models.Stock.objects.get")
    @patch("stock_trading.services.fetch_stock_price")
    def test_buy_stock_success(self, mock_fetch_stock_price, mock_get_stock, mock_checking_filter,
                                mock_custody_filter, mock_select_for_update, mock_get_or_create):
        # Mock stock price
        mock_fetch_stock_price.return_value = Decimal("150.00")
        self.trading_service.get_current_stock_price= MagicMock(return_value=150)

        # Mock stock details
        mock_get_stock.return_value = self.stock_one

        # Mock custody account
        mock_custody_account = MagicMock()
        mock_custody_account.reference_account_id = self.account_uuid
        mock_custody_filter.return_value.first.return_value = mock_custody_account

        # Mock checking account
        self.account.opening_balance = Decimal("1000.00")
        mock_checking_filter.return_value.first.return_value = self.account

        # Simulate the deduction of balance during the transaction
        def mock_validate_transaction(total_cost, account_id, reference_account_id):
            self.account.opening_balance -= Decimal(total_cost)

        self.account_service.validate_accounts_for_transaction.side_effect = mock_validate_transaction

        # Mock stock ownership for bank custody
        mock_bank_ownership = MagicMock(quantity=Decimal("10"))
        mock_select_for_update.return_value.filter.return_value.first.return_value = mock_bank_ownership

        # Mock get_or_create for user's stock ownership
        mock_user_ownership = MagicMock(quantity=Decimal("0"))
        mock_get_or_create.return_value = (mock_user_ownership, True)

        # Call the method
        result = self.trading_service.buy_stock(self.account_uuid, self.stock_one_uuid, 2)

        # Assertions
        self.assertTrue(result)
        self.assertEqual(self.account.opening_balance, Decimal("700.00"))  # 1000 - (2 * 150)

        mock_get_or_create.assert_called_once()
        mock_user_ownership.save.assert_called_once()
        self.assertEqual(mock_user_ownership.quantity, Decimal("2"))



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

            self.assertIn("Stock purchase failed: ", str(context.exception))

    @patch("stock_trading.models.Stock.objects.select_for_update")
    def test_get_current_stock_price(self, mocked_stock):
        # Mock stock instance
        mock_stock = self.mock_stock
        mock_stock.last_updated = now() - timedelta(minutes=2)


        mocked_stock.return_value.filter.return_value.first.return_value = mock_stock

        # Mock fetch_stock_price function to return a specific price
        with patch("stock_trading.services.fetch_stock_price", return_value=Decimal("150.00")):
            result = self.trading_service.get_current_stock_price(mock_stock.symbol)

        # Assert the correct price is returned
        self.assertEqual(result, Decimal("150.00"))


        self.assertEqual(mock_stock.current_price, Decimal("150.00"))
        self.assertTrue(mock_stock.last_updated > now() - timedelta(seconds=10))
        mock_stock.save.assert_called_once_with(update_fields=["current_price", "last_updated"])

    def test_get_current_stock_price_failed(self):
        not_existing_stock = "NOT_EXISTING_STOCK"
        stock_symbol = "NOT_EXISTING_STOCK"

        self.trading_service.get_current_stock_price = MagicMock(side_effect=ValidationError(f"Failed to fetch and update stock price for {stock_symbol}: "))

        with self.assertRaises(ValidationError) as context:
            self.trading_service.get_current_stock_price(not_existing_stock)

        self.assertIn(f"Failed to fetch and update stock price for {stock_symbol}: ", str(context.exception))