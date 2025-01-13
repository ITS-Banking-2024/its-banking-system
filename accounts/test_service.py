import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from marshmallow import ValidationError
from uuid import uuid4

from accounts.services import AccountService
from accounts.models import Account
from accounts.models import CheckingAccount, SavingsAccount, CustodyAccount


class TestAccountService(unittest.TestCase):
    def setUp(self):

        self.transaction_service = Mock()
        self.account_service = AccountService(self.transaction_service)

        self.mock_checking_account = patch('accounts.services.CheckingAccount').start()
        self.mock_savings_account = patch('accounts.services.SavingsAccount').start()
        self.mock_custody_account = patch('accounts.services.CustodyAccount').start()

        self.account_one = Mock()
        self.account_one.account_id = '123e4567-e89b-12d3-a456-426614174000'
        self.account_one.customer_id = 1
        self.account_one.opening_balance = 1000.00

        self.account_two = Mock()
        self.account_two.account_id = '123e4567-e89b-12d3-a456-426614174001'
        self.account_two.customer_id = 2
        self.account_two.opening_balance = 2000.00


    def test_get_account(self):
        # Mock the first return value to match the expected account
        self.mock_checking_account.objects.filter.return_value.first.return_value = self.account_one

        result = self.account_service.get_account('123e4567-e89b-12d3-a456-426614174000')

        self.assertEqual(result, self.account_one)
        self.mock_checking_account.objects.filter.assert_called_once_with(account_id='123e4567-e89b-12d3-a456-426614174000')

    @patch('accounts.services.AccountBase.objects.all')
    def test_get_all_accounts(self, mock_all):
        # Mock the first return value to match the expected account
        mock_all.return_value = [self.account_one, self.account_two]

        result = self.account_service.get_all_accounts()

        mock_all.assert_called_once()

        self.assertEqual(result, [self.account_one, self.account_two])

    @patch('accounts.services.AccountBase.objects.filter')
    def test_get_accounts_by_customer_id(self, mock_filter):
        # Mock the first return value to match the expected account
        mock_filter.return_value = [self.account_one]

        result = self.account_service.get_accounts_by_customer_id(1)

        mock_filter.assert_called_once_with(customer_id=1)

        self.assertEqual(result, [self.account_one])

    @patch('accounts.services.AccountBase.objects.filter')
    def test_get_balance_no_transactions(self, mock_filter):
        mock_filter.return_value.first.return_value = self.account_one
        self.transaction_service.get_transaction_history.return_value = []

        result = self.account_service.get_balance(self.account_one.account_id)

        self.assertEqual(result, Decimal(self.account_one.opening_balance).quantize(Decimal("0.01")))

    @patch('accounts.services.AccountBase.objects.filter')
    def test_get_balance_invalid_transaction(self, mock_filter):
        mock_filter.return_value.first.return_value = self.account_one
        self.transaction_service.get_transaction_history.return_value = [
            {"sending_account_id": "invalid_id", "receiving_account_id": "another_invalid_id", "amount": "100.00"},
        ]

        with self.assertRaises(ValidationError):
            self.account_service.get_balance(self.account_one.account_id)

    @patch('accounts.services.AccountBase.objects.filter')
    def test_get_balance_with_transactions(self, mock_filter):
        mock_filter.return_value.first.return_value = self.account_one
        self.transaction_service.get_transaction_history.return_value = [
            {"sending_account_id": self.account_one.account_id, "receiving_account_id": self.account_two.account_id, "amount": "100.00"},
            {"sending_account_id": self.account_two.account_id, "receiving_account_id": self.account_one.account_id, "amount": "50.00"},
        ]

        result = self.account_service.get_balance(self.account_one.account_id)

        self.assertEqual(result, Decimal("950.00"))
        assert self.transaction_service.get_transaction_history.call_count == 1

    @patch('accounts.services.AccountBase.objects.filter')
    def test_validate_accounts_for_transaction(self, mock_filter):
        self.mock_checking_account.objects.filter.return_value.first.return_value = self.account_one
        self.mock_checking_account.objects.filter.return_value.first.return_value = self.account_two

        self.assertTrue(self.account_service.validate_accounts_for_transaction(100.00, self.account_one.account_id, self.account_two.account_id))


    @patch('accounts.services.AccountBase.objects.filter')
    def test_validate_accounts_for_transaction_invalid_sending_account(self, mock_filter):
        # Simulate non-existent sending account and valid receiving account
        def filter_side_effect(**kwargs):
            if kwargs.get("account_id") == self.account_two.account_id:
                mock_qs = Mock()
                mock_qs.first.return_value = self.account_two
                return mock_qs
            else:
                mock_qs = Mock()
                mock_qs.first.return_value = None
                return mock_qs

        mock_filter.side_effect = filter_side_effect

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_accounts_for_transaction(Decimal("100.00"), "non_existent_sending_account_id", self.account_two.account_id)

        self.assertEqual(str(context.exception), "Sending account with ID non_existent_sending_account_id does not exist.")

    @patch('accounts.services.AccountBase.objects.filter')
    def test_validate_accounts_for_transaction_invalid_receiving_account(self, mock_filter):
        # Simulate non-existent sending account and valid receiving account
        def filter_side_effect(**kwargs):
            if kwargs.get("account_id") == self.account_one.account_id:
                mock_qs = Mock()
                mock_qs.first.return_value = self.account_one
                return mock_qs
            else:
                mock_qs = Mock()
                mock_qs.first.return_value = None
                return mock_qs

        mock_filter.side_effect = filter_side_effect

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_accounts_for_transaction(Decimal("100.00"), self.account_one.account_id,"non_existent_sending_account_id")

        self.assertEqual(str(context.exception),"Receiving account with ID non_existent_sending_account_id does not exist.")

    @patch('accounts.services.AccountBase.objects.filter')
    def test_validate_accounts_for_transaction_negative_amount(self, mock_filter):
        self.mock_checking_account.objects.filter.return_value.first.return_value = self.account_one
        self.mock_checking_account.objects.filter.return_value.first.return_value = self.account_two

        with self.assertRaises(ValidationError) as context:
            self.assertTrue(self.account_service.validate_accounts_for_transaction(-100.00, self.account_one.account_id, self.account_two.account_id))

        self.assertEqual(str(context.exception), "Transaction amount must be greater than zero.")


    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.transaction.atomic')
    def test_deposit_savings(self, mock_atomic, mock_filter):
        # Mock a valid savings account with a reference account
        savings_account_mock = Mock()
        savings_account_mock.account_id = self.account_one.account_id

        # Mock the reference account -> in this scenario account_two will be the reference account
        savings_account_mock.reference_account = self.account_two

        mock_filter.return_value.first.return_value = savings_account_mock
        self.transaction_service.create_new_transaction.return_value = True

        self.account_service.deposit_savings(self.account_one.account_id, 100.00)

        mock_filter.assert_called_once_with(account_id=self.account_one.account_id)

        self.transaction_service.create_new_transaction.assert_called_once_with(amount=100.00, sending_account_id=self.account_two.account_id, receiving_account_id=self.account_one.account_id)

        # Ensure atomic transaction was used
        self.assertTrue(mock_atomic.called)

    def test_deposit_savings_invalid_amount(self):
        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(self.account_one.account_id, -100.00)

        self.assertEqual(str(context.exception), "Deposit amount must be greater than zero.")

    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.transaction.atomic')
    def test_deposit_savings_no_savings_account(self, mock_atomic, mock_filter):
        # Mock a valid savings account with a reference account
        savings_account_mock = Mock()
        savings_account_mock.account_id = self.account_one.account_id

        # Mock the reference account -> in this scenario there are no reference account
        savings_account_mock.reference_account.account_id = "non_existent_savings_account_id"

        mock_filter.return_value.first.return_value = None

        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(self.account_one.account_id, 100.00)

        self.assertEqual(str(context.exception), f"Account with ID {self.account_one.account_id} does not exist.")

    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.transaction.atomic')
    def test_deposit_savings_failure(self, mock_atomic, mock_filter):
        # Mock a valid savings account with a reference account
        savings_account_mock = Mock()
        savings_account_mock.account_id = self.account_one.account_id

        # Mock the reference account -> in this scenario account_two will be the reference account
        savings_account_mock.reference_account = self.account_two

        mock_filter.return_value.first.return_value = savings_account_mock

        # Mock the error
        self.transaction_service.create_new_transaction.side_effect = Exception("None")

        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(self.account_one.account_id, 100.00)

        self.assertEqual(str(context.exception), "Deposit failed: None")

        assert mock_atomic.called

    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.AccountService.get_balance')
    def test_withdraw_savings_insufficient_funds(self, mock_get_balance, mock_filter):
        # Mock the balance to simulate insufficient funds
        mock_get_balance.return_value = 1000.00

        # Mock the savings account
        savings_account_mock = Mock()
        savings_account_mock.account_id = self.account_one.account_id
        savings_account_mock.reference_account = self.account_two
        mock_filter.return_value.first.return_value = savings_account_mock

        # Attempt to withdraw an amount greater than the balance
        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(savings_account_mock.account_id, 20000.00)

        self.assertEqual(str(context.exception), f"Insufficient funds (1000.0 EUR) in account: {self.account_one.account_id} to withdraw 20000.0 EUR")

        # Ensure the mocks were called
        mock_get_balance.called_with(savings_account_mock.account_id)
        mock_filter.called_with(account_id=savings_account_mock.account_id)

    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.AccountService.get_balance')
    def test_withdraw_savings_negative_amount(self, mock_get_balance, mock_filter):
    # Mock the balance to simulate insufficient funds
        mock_get_balance.return_value = 1000.00

        # Mock the savings account
        savings_account_mock = Mock()
        savings_account_mock.account_id = self.account_one.account_id
        savings_account_mock.reference_account = self.account_two
        mock_filter.return_value.first.return_value = savings_account_mock

        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(self.account_one.account_id, -100.00)

        self.assertEqual(str(context.exception), "Withdrawal amount must be greater than zero.")


    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.AccountService.get_balance')
    def test_withdraw_savings_non_existent_account(self, mock_get_balance, mock_filter):
        # Mock the balance to return a float value
        mock_get_balance.return_value = 1000.00

        # Mock the savings account to simulate a non-existent account
        mock_filter.return_value.first.return_value = None

        # Generate a random UUID for the account
        random_account_id = str(uuid4())

        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(random_account_id, 100.00)
        self.assertEqual(str(context.exception),f"Savings account with ID {random_account_id} does not exist.")


    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.transaction.atomic')
    @patch('accounts.services.AccountService.get_balance')
    def test_withdraw_savings(self, mock_get_balance, mock_atomic, mock_filter):
        # Mock the balance to simulate sufficient funds
        mock_get_balance.return_value = 1000.00

        # Mock a valid savings account with reference account
        savings_account_mock = Mock()
        savings_account_mock.account_id = str(uuid4())
        savings_account_mock.reference_account = self.account_two

        mock_filter.return_value.first.return_value = savings_account_mock
        self.transaction_service.create_new_transaction.return_value = True

        # Call the withdraw_savings method
        self.account_service.withdraw_savings(savings_account_mock.account_id, 100.00)

        # Assert the filter method was called with the correct account_id
        mock_filter.assert_called_once_with(account_id=savings_account_mock.account_id)

        # Assert the transaction was created with correct parameters
        self.transaction_service.create_new_transaction.assert_called_once_with(
            amount=100.00,
            sending_account_id=savings_account_mock.account_id,
            receiving_account_id=self.account_two.account_id,
        )

        # Ensure atomic transaction was used
        self.assertTrue(mock_atomic.called)


    @patch('accounts.services.SavingsAccount.objects.filter')
    @patch('accounts.services.transaction.atomic')
    @patch('accounts.services.AccountService.get_balance')
    def test_withdraw_savings_failure(self, mock_get_balance, mock_atomic, mock_filter):
        # Mock the balance to simulate sufficient funds
        mock_get_balance.return_value = 1000.00

        # Mock a valid savings account with reference account
        savings_account_mock = Mock()
        savings_account_mock.account_id = str(uuid4())
        savings_account_mock.reference_account = self.account_two

        mock_filter.return_value.first.return_value = savings_account_mock
        self.transaction_service.create_new_transaction.side_effect = Exception("None")

        # Call the withdraw_savings method and expect a ValidationError
        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(savings_account_mock.account_id, 100.00)

        # Assert the exception message
        self.assertEqual(str(context.exception), "Withdrawal failed: None")

        # Ensure atomic transaction was used
        self.assertTrue(mock_atomic.called)



    def tearDown(self):
        patch.stopall()


