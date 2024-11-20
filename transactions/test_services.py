import unittest
from unittest.mock import patch, Mock
from transactions.services import BankingServiceImplI
from datetime import datetime
from accounts.models import AccountBase


class TestTransactionServiceImplI(unittest.TestCase):
    def setUp(self):
        # initialize the BankingServiceImplI instance
        self.transaction_service = BankingServiceImplI()

        # patch Transaction model and account model instances
        self.mock_transaction_model = patch('transactions.models.Transaction').start()
        self.mock_account_model = patch('accounts.models.Account').start()

        # Mock sending account
        self.sending_account = Mock(spec=AccountBase)
        self.sending_account.save = Mock()

        # Mock receiving account
        self.receiving_account = Mock(spec=AccountBase)
        self.receiving_account.save = Mock()

        # Mock the creation of a transaction
        self.mock_transaction = Mock()
        self.mock_transaction_model.objects.create.return_value = self.mock_transaction

    def tearDown(self):
        patch.stopall()

    """
    def test_create_transaction(self):

        with patch('transactions.services.Transaction.objects.create', return_value=self.mock_transaction) as mock_create:
            transaction = self.transaction_service.create_transaction(
                sending_account=self.sending_account,
                receiving_account=self.receiving_account,
                amount=100.0
            )

            # check if we created a transaction
            self.assertIsNotNone(transaction)
            mock_create.assert_called_once()


            # check if we saved the accounts
            self.sending_account.save.assert_called_once()
            self.receiving_account.save.assert_called_once()

    def test_create_transaction_insufficient_funds(self):
        # create a transaction
        with self.assertRaises(ValueError):
            transaction = self.transaction_service.create_transaction(
                sending_account=self.sending_account,
                receiving_account=self.receiving_account,
                amount=10000.0
            )
        # check thath transation is created
        self.mock_transaction_model.objects.create.assert_not_called()


        # check if the save method was called
        self.sending_account.save.assert_not_called()
        self.receiving_account.save.assert_not_called()
    """