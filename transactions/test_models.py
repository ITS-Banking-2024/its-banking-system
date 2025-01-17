from django.test import TestCase
from transactions.models import Transaction, StockTransaction, ATMTransaction
from transactions.settings import STOCK_MODEL
from django.apps import apps
from uuid import uuid4


class TestTransactions(TestCase):

    def setUp(self) -> None:

        # Get the concrete Stock model from STOCK_MODEL
        Stock = apps.get_model(STOCK_MODEL)

        # Create a stock instance
        self.stock = Stock.objects.create(
            stockID=uuid4(),
            stock_name='Test Stock',
            current_price=1000.00
        )

    def test_new_transaction(self) -> None:

        sending_account_id = uuid4()
        receiving_account_id = uuid4()
        amount = 1000

        transaction = Transaction.objects.create(
            transaction_id=uuid4(),
            sending_account_id=sending_account_id,
            receiving_account_id=receiving_account_id,
            amount=amount,
        )

        self.assertIsNotNone(transaction)
        self.assertIsNotNone(transaction.transaction_id)
        self.assertEqual(transaction.sending_account_id, sending_account_id)
        self.assertEqual(transaction.receiving_account_id, receiving_account_id)
        self.assertEqual(transaction.amount, amount)
        self.assertEqual(str(transaction), f"Transaction {transaction.transaction_id} of amount {amount}")

    def test_new_stock_transaction(self) -> None:
        # Create a new stock transaction
        sending_account_id = uuid4()
        receiving_account_id = uuid4()
        amount = 1000

        stock_transaction = StockTransaction.objects.create(
            sending_account_id=sending_account_id,
            receiving_account_id=receiving_account_id,
            amount=amount,
            stockId=self.stock.stockID,

            quantity=10,
            transaction_type='buy'
        )

        # Assert that the transaction was created successfully
        self.assertIsNotNone(stock_transaction)
        self.assertEqual(stock_transaction.sending_account_id, sending_account_id)
        self.assertEqual(stock_transaction.receiving_account_id, receiving_account_id)
        self.assertEqual(stock_transaction.amount, amount)
        self.assertEqual(stock_transaction.stockId, self.stock.stockID)
        self.assertEqual(stock_transaction.quantity, 10)
        self.assertEqual(stock_transaction.transaction_type, 'buy')
        self.assertEqual(str(stock_transaction), f"Transaction {stock_transaction.transaction_id} of amount {stock_transaction.amount}")

    def test_new_atm_transaction(self) -> None:
        # Create a new ATM transaction
        sending_account_id = uuid4()
        receiving_account_id = uuid4()
        amount = 1000

        atm_transaction = ATMTransaction.objects.create(
            sending_account_id=sending_account_id,
            receiving_account_id=receiving_account_id,
            amount=amount
        )

        # Assert that the transaction was created successfully
        self.assertIsNotNone(atm_transaction)
        self.assertEqual(atm_transaction.sending_account_id, sending_account_id)
        self.assertEqual(atm_transaction.receiving_account_id, receiving_account_id)
        self.assertEqual(atm_transaction.amount, amount)
        self.assertEqual(str(atm_transaction), f"Transaction {atm_transaction.transaction_id} of amount {atm_transaction.amount}")

