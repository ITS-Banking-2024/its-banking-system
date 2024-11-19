import unittest
from unittest.mock import Mock, patch

from accounts.services import AccountService
from accounts.models import Account

class TestAccountService(unittest.TestCase):
    def setUp(self):
        self.account_service = AccountService()

        self.mock_checking_account = patch('accounts.models.CheckingAccount').start()
        self.mock_savings_account = patch('accounts.models.SavingsAccount').start()
        self.mock_custody_account = patch('accounts.models.CustodyAccount').start()

    def tearDown(self):
        patch.stopall()


