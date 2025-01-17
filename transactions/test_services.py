import unittest
from unittest.mock import patch, Mock
from transactions.services import TransactionService
from datetime import datetime
from accounts.models import AccountBase


class TestTransactionServiceImplI(unittest.TestCase):
    def setUp(self):
        # initialize the TransactionService instance
        self.transaction_service = TransactionService()

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
