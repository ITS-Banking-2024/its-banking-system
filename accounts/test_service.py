import unittest
from unittest.mock import Mock, patch

from accounts.services import AccountService
from accounts.models import Account

class TestAccountService(unittest.TestCase):
    def setUp(self):
        self.account_service = AccountService()

        self.mock_account_model = patch('accounts.services.Account').start()
        self.mock_checking_account = patch('accounts.services.CheckingAccount').start()
        self.mock_savings_account = patch('accounts.services.SavingsAccount').start()
        self.mock_custody_account = patch('accounts.services.CustodyAccount').start()


    def tearDown(self):
        patch.stopall()

    def test_get_all_accounts(self):
        # mock the return value of Account.objects.all()
        self.mock_account_model.objects.all.return_value = [Mock(spec=Account), Mock(spec=Account)]


        accounts = self.account_service.get_all_accounts()
        self.assertEqual(len(accounts), 2)  # we are expecting to get 2 accounts, cause we mocked it this way
        self.mock_account_model.objects.all.assert_called_once()  # make sure that Account.objects.all() was called once

    def test_get_account_balance(self):
        # mock account with a balance of 100.00
        mock_account = Mock(spec=Account)
        mock_account.balance = 100.00

        # call get_account_balance method
        balance = self.account_service.get_account_balance(mock_account)
        self.assertEqual(balance, 100.00)

    def test_get_by_id_existing_account(self):
        # mock the return value of Account.objects.get(id) to return a mock account
        mock_account = Mock(spec=Account)
        self.mock_account_model.objects.get.return_value = mock_account

        # call method get_by_id to check if it works
        account = self.account_service.get_by_id(1)
        self.assertEqual(account, mock_account)
        self.mock_account_model.objects.get.assert_called_once_with(id=1)
