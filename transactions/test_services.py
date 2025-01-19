import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from uuid import uuid4
from django.core.exceptions import ValidationError
from transactions.services import TransactionService
from transactions.models import Transaction, StockTransaction, ATMTransaction

class TestTransactionService(unittest.TestCase):
    def setUp(self):
        # Initialize the TransactionService instance
        self.transaction_service = TransactionService()

        # Patch Transaction and StockTransaction models
        self.mock_transaction_model = patch('transactions.models.Transaction').start()
        self.mock_stock_transaction_model = patch('transactions.models.StockTransaction').start()
        self.mock_atm_transaction_model = patch('transactions.models.ATMTransaction').start()

        # Mock sending and receiving accounts
        self.sending_account_id = uuid4()
        self.receiving_account_id = uuid4()
        self.account_id = uuid4()
        self.second_account_id = uuid4()
        self.stock_receiving_account_id = uuid4()

        # Mock a transaction instance
        self.mock_transaction = Mock()
        self.mock_transaction.transaction_id = uuid4()
        self.mock_transaction.date = datetime.now()
        self.mock_transaction.amount = 100.0
        self.mock_transaction.sending_account_id = self.sending_account_id
        self.mock_transaction.receiving_account_id = self.receiving_account_id

        self.mock_stock_transaction_model.objects.create.return_value = self.mock_transaction

        # Create transactions within the last 30 and 60 days
        self.transaction_30_days = Transaction.objects.create(
            transaction_id=uuid4(),
            sending_account_id=self.account_id,
            receiving_account_id=uuid4(),
            amount=100.50,
            date=datetime.now() - timedelta(days=15),
        )
        self.transaction_60_days = Transaction.objects.create(
            transaction_id=uuid4(),
            sending_account_id=self.account_id,
            receiving_account_id=uuid4(),
            amount=200.75,
            date=datetime.now() - timedelta(days=45),
        )

        # Create transactions older than 60 days
        self.transaction_old = Transaction.objects.create(
            transaction_id=uuid4(),
            sending_account_id=self.account_id,
            receiving_account_id=uuid4(),
            amount=300.25,
            date=datetime.now() - timedelta(days=90),
        )

        self.transaction_1_uuid = uuid4()
        self.transaction_2_uuid = uuid4()
        self.transaction_3_uuid = uuid4()

        # Create stock transactions within the last 30 and 60 days
        self.stock_transaction_30_days = StockTransaction.objects.create(
            transaction_id=self.transaction_1_uuid,
            stockId=uuid4(),
            transaction_type="Buy",
            quantity=10,
            amount=1500.50,
            date=datetime.now() - timedelta(days=15),
            sending_account_id=self.second_account_id,
            receiving_account_id=self.stock_receiving_account_id,
        )

        self.stock_transaction_60_days = StockTransaction.objects.create(
            transaction_id=self.transaction_2_uuid,
            stockId=uuid4(),
            transaction_type="Sell",
            quantity=5,
            amount=2500.75,
            date=datetime.now() - timedelta(days=45),
            sending_account_id=self.second_account_id,
            receiving_account_id=self.stock_receiving_account_id,
        )

        # Create stock transactions older than 60 days
        self.stock_transaction_old = StockTransaction.objects.create(
            transaction_id=self.transaction_3_uuid,
            stockId=uuid4(),
            transaction_type="Buy",
            quantity=20,
            amount=3000.25,
            date=datetime.now() - timedelta(days=90),
            sending_account_id=self.second_account_id,
            receiving_account_id=self.stock_receiving_account_id,
        )

        # Account for the transaction
        self.mock_atm_sending_account_id = uuid4()

        self.mock_atm_transaction=Mock()
        self.mock_atm_transaction.sending_account_id = self.mock_atm_sending_account_id
        self.mock_atm_transaction.amount = 100.0
        self.mock_atm_transaction.atmId = uuid4()

        self.mock_atm_transaction_model.objects.create.return_value = self.mock_atm_transaction



    def test_create_new_transaction_success(self):
        self.mock_transaction_model.objects.create.return_value = self.mock_transaction

        result = self.transaction_service.create_new_transaction(
            amount=100.0,
            sending_account_id=self.sending_account_id,
            receiving_account_id=self.receiving_account_id,
        )

        self.assertTrue(result)
        self.assertEqual(self.mock_transaction.amount, 100.0)
        self.assertEqual(self.mock_transaction.sending_account_id, self.sending_account_id)
        self.assertEqual(self.mock_transaction.receiving_account_id, self.receiving_account_id)

    def test_create_new_transaction_failure(self):
        self.transaction_service.create_new_transaction = Mock(side_effect=ValidationError("Transaction failed"))

        with self.assertRaises(ValidationError) as context:
            self.transaction_service.create_new_transaction(
                amount=100.0,
                sending_account_id=self.sending_account_id,
                receiving_account_id=self.receiving_account_id,
            )

        self.assertEqual(str(context.exception), "['Transaction failed']")

    def test_create_new_stock_transaction_success(self):
        self.mock_stock_transaction = Mock()
        self.mock_stock_transaction.transaction_id = uuid4()
        self.mock_stock_transaction.date = datetime.now()
        self.mock_stock_transaction.amount = 100.0
        self.mock_stock_transaction.sending_account_id = self.sending_account_id
        self.mock_stock_transaction.receiving_account_id = self.receiving_account_id
        self.mock_stock_transaction.stock_id = uuid4()
        self.mock_stock_transaction.quantity = 10
        self.mock_stock_transaction.transaction_type = "buy"

        self.mock_stock_transaction_model.objects.create.return_value = self.mock_stock_transaction

        result = self.transaction_service.create_new_stock_transaction(
            amount=100.0,
            sending_account_id=self.sending_account_id,
            receiving_account_id=self.receiving_account_id,
            stock_id=uuid4(),
            quantity=10,
            transaction_type="buy"
        )

        self.assertTrue(result)
        self.assertEqual(self.mock_stock_transaction.amount, 100.0)
        self.assertEqual(self.mock_stock_transaction.sending_account_id, self.sending_account_id)
        self.assertEqual(self.mock_stock_transaction.receiving_account_id, self.receiving_account_id)
        self.assertEqual(self.mock_stock_transaction.stock_id, self.mock_stock_transaction.stock_id)
        self.assertEqual(self.mock_stock_transaction.quantity, 10)
        self.assertEqual(self.mock_stock_transaction.transaction_type, "buy")

    def test_create_new_stock_transaction_failure(self):
        self.transaction_service.create_new_stock_transaction = Mock(side_effect=ValidationError("Transaction failed"))

        with self.assertRaises(ValidationError) as context:
            self.transaction_service.create_new_stock_transaction(
                amount=100.0,
                sending_account_id=self.sending_account_id,
                receiving_account_id=self.receiving_account_id,
                stock_id=uuid4(),
                quantity=10,
                transaction_type="buy"
            )

        self.assertEqual(str(context.exception), "['Transaction failed']")

    def test_get_transaction_history_invalid_timeframe(self):
        with self.assertRaises(ValueError) as context:
            self.transaction_service.get_transaction_history(self.sending_account_id, "invalid_timeframe")

        self.assertEqual(str(context.exception), "Invalid timeframe. Valid options are '30_days', '60_days', or 'all_time'.")

    def test_get_transaction_history_empty_list(self):
        self.mock_transaction_model.objects.filter.return_value = []

        result = self.transaction_service.get_transaction_history(self.sending_account_id, "all_time")

        self.assertEqual(result, [])


    def test_get_transaction_history_30_days(self):
        result = self.transaction_service.get_transaction_history(account_id=self.account_id, timeframe="30_days")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["transaction_id"], str(self.transaction_30_days.transaction_id))

    def test_get_transaction_history_60_days(self):
        result = self.transaction_service.get_transaction_history(account_id=self.account_id, timeframe="60_days")

        self.assertEqual(len(result), 2)
        transaction_ids = [tx["transaction_id"] for tx in result]
        self.assertIn(str(self.transaction_30_days.transaction_id), transaction_ids)
        self.assertIn(str(self.transaction_60_days.transaction_id), transaction_ids)

    def test_get_transaction_history_all_time(self):
        result = self.transaction_service.get_transaction_history(account_id=self.account_id, timeframe="all_time")

        self.assertEqual(len(result), 3)
        transaction_ids = [tx["transaction_id"] for tx in result]
        self.assertIn(str(self.transaction_30_days.transaction_id), transaction_ids)
        self.assertIn(str(self.transaction_60_days.transaction_id), transaction_ids)
        self.assertIn(str(self.transaction_old.transaction_id), transaction_ids)

    def test_get_stock_transaction_history_30_days(self):
        result = self.transaction_service.get_stock_transaction_history(account_id=self.second_account_id, timeframe="30_days")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["transaction_id"], str(self.stock_transaction_30_days.transaction_id))

    def test_get_stock_transaction_history_60_days(self):
        result = self.transaction_service.get_stock_transaction_history(account_id=self.second_account_id, timeframe="60_days")

        self.assertEqual(len(result), 2)
        transaction_ids = [tx["transaction_id"] for tx in result]
        self.assertIn(str(self.stock_transaction_30_days.transaction_id), transaction_ids)
        self.assertIn(str(self.stock_transaction_60_days.transaction_id), transaction_ids)

    def test_get_stock_transaction_history_all_time(self):
        result = self.transaction_service.get_stock_transaction_history(account_id=self.second_account_id, timeframe="all_time")

        self.assertEqual(len(result), 3)
        transaction_ids = [tx["transaction_id"] for tx in result]
        self.assertIn(str(self.stock_transaction_30_days.transaction_id), transaction_ids)
        self.assertIn(str(self.stock_transaction_60_days.transaction_id), transaction_ids)
        self.assertIn(str(self.stock_transaction_old.transaction_id), transaction_ids)

    def test_get_stock_transaction_history_invalid_timeframe(self):
        with self.assertRaises(ValueError):
            self.transaction_service.get_stock_transaction_history(account_id=self.second_account_id, timeframe="invalid_timeframe")


    def test_new_atm_transaction_success(self):

        result = self.transaction_service.create_new_atm_transaction(
            amount=100.0,
            account_id=self.mock_atm_transaction.sending_account_id,
            atm_id=uuid4())

        self.assertTrue(result)
        self.assertEqual(self.mock_atm_transaction.amount, 100.0)
        self.assertEqual(self.mock_atm_transaction.sending_account_id, self.mock_atm_transaction.sending_account_id)

    def test_new_atm_transaction_failure(self):
        self.transaction_service.create_new_atm_transaction = Mock(side_effect=ValidationError("Atm transaction failed"))

        with self.assertRaises(ValidationError) as context:
            self.transaction_service.create_new_atm_transaction(
                amount=100.0,
                account_id=self.mock_atm_transaction.sending_account_id,
                atm_id=uuid4()
            )

        self.assertEqual(str(context.exception), "['Atm transaction failed']")

    def tearDown(self):
        patch.stopall()