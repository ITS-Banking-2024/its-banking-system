import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from marshmallow import ValidationError
from uuid import uuid4, UUID

from accounts.services import AccountService
from accounts.models import Account
from accounts.models import CheckingAccount, SavingsAccount, CustodyAccount


class FakeCustodyAccount:
    pass

class FakeCheckingAccount:
    pass

class FakeSavingsAccount:
    pass

class TestAccountService(unittest.TestCase):
    def setUp(self):

        self.transaction_service = Mock()
        self.account_service = AccountService(self.transaction_service)

        self.mock_checking_account = patch('accounts.services.CheckingAccount').start()
        self.mock_savings_account = patch('accounts.services.SavingsAccount').start()
        self.mock_custody_account = patch('accounts.services.CustodyAccount').start()

        self.account_one = Mock(spec=CheckingAccount)
        self.account_one.account_id = '123e4567-e89b-12d3-a456-426614174000'
        self.account_one.customer_id = 1
        self.account_one.opening_balance = 1000.00
        self.account_one.type = "checking"

        self.account_two = Mock()
        self.account_two.account_id = '123e4567-e89b-12d3-a456-426614174001'
        self.account_two.customer_id = 2
        self.account_two.opening_balance = 2000.00
        self.account_two.type = "savings"


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

    @patch("accounts.services.CustodyAccount")
    def test_get_bank_custody_account_not_found(self, mock_custody_account):
        # Mock CustodyAccount.DoesNotExist as a subclass of BaseException
        mock_custody_account.DoesNotExist = Exception

        # Mock the get() method to raise DoesNotExist
        mock_custody_account.objects.get.side_effect = mock_custody_account.DoesNotExist

        # Call the method and assert the exception
        with self.assertRaises(ValueError) as context:
            self.account_service.get_bank_custody_account()

        # Assertions
        self.assertEqual(
            str(context.exception),
            "Bank custody account is not set up. Please check the database configuration."
        )
        mock_custody_account.objects.get.assert_called_once_with(unique_identifier="bank_custody_account")


    @patch("accounts.services.CustodyAccount")
    def test_get_bank_custody_account_found(self, mock_custody_account):
        # Mock a CustodyAccount object
        mock_bank_custody_account = MagicMock()
        mock_custody_account.objects.get.return_value = mock_bank_custody_account

        # Call the method
        result = self.account_service.get_bank_custody_account()

        # Assertions
        self.assertEqual(result, mock_bank_custody_account)
        mock_custody_account.objects.get.assert_called_once_with(unique_identifier="bank_custody_account")

    @patch("accounts.services.CustodyAccount")
    def test_get_balance_account_custody(self, MockCustodyAccount):

        custody_account = FakeCustodyAccount()
        custody_account.account_id = '123e4567-e89b-12d3-a456-426614174002'

        # Mock get_account to return the custody account
        self.account_service.get_account = Mock(return_value=custody_account)

        # Temporarily replace CustodyAccount in the tested function's scope
        with patch("accounts.services.CustodyAccount", FakeCustodyAccount):
            # Call the get_balance method
            balance = self.account_service.get_balance(custody_account.account_id)

            # Assertions
            self.assertEqual(balance, 0.00)  # Custody accounts always return 0
            self.transaction_service.get_transaction_history.assert_not_called()

    def test_get_balance_checking_account(self):
            # Mock a checking account with opening balance and transaction history
            checking_account = FakeCheckingAccount()
            checking_account.account_id = UUID("123e4567-e89b-12d3-a456-426614174003")
            checking_account.opening_balance = 1000.0

            # Mock get_account to return the checking account
            self.account_service.get_account = Mock(return_value=checking_account)

            # Mock transaction history with the correct structure
            self.transaction_service.get_transaction_history = Mock(return_value=[
                {
                    "transaction_id": "txn-001",
                    "sending_account_id": str(checking_account.account_id),
                    "receiving_account_id": "another-account-id",
                    "amount": "100.0",
                    "date": "2025-01-16 12:00:00",
                },
                {
                    "transaction_id": "txn-002",
                    "sending_account_id": "another-account-id",
                    "receiving_account_id": str(checking_account.account_id),
                    "amount": "50.0",
                    "date": "2025-01-16 12:30:00",
                },
            ])

            # Mock isinstance for CheckingAccount
            with patch("accounts.services.isinstance", lambda obj, cls: isinstance(obj, FakeCheckingAccount) if cls is CheckingAccount else False):
                # Call the get_balance method
                balance = self.account_service.get_balance(checking_account.account_id)

                # Assertions
                self.assertEqual(balance, 950.0)  # (1000 - 100 + 50 = 950)
                self.transaction_service.get_transaction_history.assert_called_once_with(checking_account.account_id, "all_time")

    def test_get_balance_checking_account_no_history(self):
        # Mock a checking account with opening balance and transaction history
        checking_account = FakeCheckingAccount()
        checking_account.account_id = UUID("123e4567-e89b-12d3-a456-426614174003")
        checking_account.opening_balance = 1000.0

        # Mock get_account to return the checking account
        self.account_service.get_account = Mock(return_value=checking_account)

        # Mock transaction history with the correct structure
        self.transaction_service.get_transaction_history = Mock(return_value=[])
        # Mock isinstance for CheckingAccount
        with patch("accounts.services.isinstance", lambda obj, cls: isinstance(obj, FakeCheckingAccount) if cls is CheckingAccount else False):
            # Call the get_balance method
            balance = self.account_service.get_balance(checking_account.account_id)

            # Assertions
            self.assertEqual(balance, 1000)
            self.transaction_service.get_transaction_history.assert_called_once_with(checking_account.account_id, "all_time")

    def test_get_balance_checking_account_transaction_not_made_with_this_account(self):
        # Mock a checking account with opening balance and transaction history
        checking_account = FakeCheckingAccount()
        checking_account.account_id = UUID("123e4567-e89b-12d3-a456-426614174003")
        checking_account.opening_balance = 1000.0

        # Mock get_account to return the checking account
        self.account_service.get_account = Mock(return_value=checking_account)

        # Mock transaction history with the correct structure
        self.transaction_service.get_transaction_history = Mock(return_value=[
            {
                "transaction_id": "txn-001",
                "sending_account_id": "another-account-id",
                "receiving_account_id": "another-account-id",
                "amount": "100.0",
                "date": "2025-01-16 12:00:00",
            },
            {
                "transaction_id": "txn-002",
                "sending_account_id": "another-account-id",
                "receiving_account_id": "another-account-id",
                "amount": "50.0",
                "date": "2025-01-16 12:30:00",
            },
        ])

        # Mock isinstance for CheckingAccount
        with patch("accounts.services.isinstance", lambda obj, cls: isinstance(obj, FakeCheckingAccount) if cls is CheckingAccount else False):
            with self.assertRaises(ValidationError) as context:
                balance = self.account_service.get_balance(checking_account.account_id)

            self.assertEqual(str(context.exception), "Transaction not made with this account")

    def test_get_account_totals(self):
            checking_account = FakeCheckingAccount()
            checking_account.account_id = UUID("123e4567-e89b-12d3-a456-426614174003")
            checking_account.opening_balance = 1000.0

            # Mock get_account to return the checking account
            self.account_service.get_account = Mock(return_value=checking_account)

            self.transaction_service.get_transaction_history = Mock(return_value=[
                {
                    "transaction_id": "txn-001",
                    "sending_account_id": str(checking_account.account_id),
                    "receiving_account_id": "another-account-id",
                    "amount": "100.0",
                    "date": "2025-01-16 12:00:00",
                },
                {
                    "transaction_id": "txn-002",
                    "sending_account_id": "another-account-id",
                    "receiving_account_id": str(checking_account.account_id),
                    "amount": "50.0",
                    "date": "2025-01-16 12:30:00",
                },
            ])

            result = self.account_service.get_account_totals(checking_account.account_id, "all_time")

            self.assertEqual(result, {"total_sent": 100.0, "total_received": 50.0})

    def test_get_account_totals_rouge_transaction(self):
        checking_account = FakeCheckingAccount()
        checking_account.account_id = UUID("123e4567-e89b-12d3-a456-426614174003")
        checking_account.opening_balance = 1000.0

        # Mock get_account to return the checking account
        self.account_service.get_account = Mock(return_value=checking_account)

        self.transaction_service.get_transaction_history = Mock(return_value=[
            {
                "transaction_id": "txn-001",
                "sending_account_id": "another-account-id",
                "receiving_account_id": "another-account-id",
                "amount": "100.0",
                "date": "2025-01-16 12:00:00",
            },
            {
                "transaction_id": "txn-002",
                "sending_account_id": "another-account-id",
                "receiving_account_id": "another-account-id",
                "amount": "50.0",
                "date": "2025-01-16 12:30:00",
            },
        ])

        with self.assertRaises(ValidationError) as context:
            result = self.account_service.get_account_totals(checking_account.account_id, "all_time")

        self.assertEqual(str(context.exception), "Rogue transaction.")

    def test_validate_accounts_for_transaction_not_sending_account(self):
        checking_account = FakeCheckingAccount()
        checking_account.account_id = None
        checking_account.opening_balance = 1000.0

        checking_account = FakeCheckingAccount()
        checking_account.account_id = None
        checking_account.opening_balance = 1000.0


        self.account_service.get_account = Mock(return_value=None)


        invalid_sending_account_id = uuid4()

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_accounts_for_transaction(
                100.0,
                sending_account_id=invalid_sending_account_id,
                receiving_account_id=uuid4()
            )

        self.assertEqual(str(context.exception),f"Sending account with ID {invalid_sending_account_id} does not exist.")

    def test_validate_accounts_for_transaction_not_receiving_account(self):
        valid_sending_account = FakeCheckingAccount()
        valid_sending_account.account_id = uuid4()
        valid_sending_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(side_effect=[valid_sending_account, None])

        valid_sending_account_id = valid_sending_account.account_id
        invalid_receiving_account_id = uuid4()

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_accounts_for_transaction(
                100.0,
                sending_account_id=valid_sending_account_id,
                receiving_account_id=invalid_receiving_account_id
            )

        self.assertEqual(str(context.exception),f"Receiving account with ID {invalid_receiving_account_id} does not exist.")

    def test_validae_accounts_for_transaction_negative_amount(self):
        valid_first_account = FakeCheckingAccount()
        valid_first_account.account_id = uuid4()
        valid_first_account.opening_balance = 1000.0

        valid_second_account = FakeCheckingAccount()
        valid_second_account.account_id = uuid4()
        valid_second_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(side_effect=[valid_first_account, valid_second_account])

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_accounts_for_transaction(-100.0, valid_first_account.account_id, valid_second_account.account_id)

        self.assertEqual(str(context.exception), "Transaction amount must be greater than zero.")

    def test_validate_accounts_for_transaction_overdraft_limit(self):
        valid_first_account = FakeCheckingAccount()
        valid_first_account.account_id = uuid4()
        valid_first_account.opening_balance = 1000.0

        valid_second_account = FakeCheckingAccount()
        valid_second_account.account_id = uuid4()
        valid_second_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(side_effect=[valid_first_account, valid_second_account])
        self.account_service.get_balance = Mock(return_value=-1000.0)

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_accounts_for_transaction(2000.0, valid_first_account.account_id, valid_second_account.account_id)

        self.assertEqual(str(context.exception), "Overdraft limit (1000.0) overreached")

    def test_validate_accounts_for_transaction_success(self):
        valid_first_account = FakeCheckingAccount()
        valid_first_account.account_id = uuid4()
        valid_first_account.opening_balance = 1000.0

        valid_second_account = FakeCheckingAccount()
        valid_second_account.account_id = uuid4()
        valid_second_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(side_effect=[valid_first_account, valid_second_account])
        self.account_service.get_balance = Mock(return_value=1000.0)

        result = self.account_service.validate_accounts_for_transaction(500.0, valid_first_account.account_id, valid_second_account.account_id)

        self.account_service.get_account.assert_any_call(valid_first_account.account_id)
        self.account_service.get_account.assert_any_call(valid_second_account.account_id)

        self.account_service.get_balance.assert_called_once_with(valid_first_account.account_id)

        self.assertTrue(result)

    def test_deposit_savings_negative_amount(self):
        valid_savings_account = FakeCheckingAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(return_value=valid_savings_account)

        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(valid_savings_account.account_id, -100.0)

        self.assertEqual(str(context.exception), "Deposit amount must be greater than zero.")

    def test_deposit_savings_no_savings_account(self):
        valid_savings_account = FakeCheckingAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(return_value=None)

        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(valid_savings_account.account_id, 100.0)

        self.assertEqual(str(context.exception), f"Account with ID {valid_savings_account.account_id} does not exist.")

    def test_deposit_savings_no_reference_account_id(self):
        valid_savings_account = FakeCheckingAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = None

        self.account_service.get_account = Mock(return_value=valid_savings_account)

        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(valid_savings_account.account_id, 100.0)

        self.assertEqual(str(context.exception), f"Account with ID {valid_savings_account.reference_account_id} does not exist.")

    def test_deposit_savings_failure(self):
        valid_savings_account = FakeSavingsAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = uuid4()

        # Mock get_account to return the valid savings account
        self.account_service.get_account = Mock(return_value=valid_savings_account)

        # Mock create_new_transaction to raise an exception
        self.account_service.validate_accounts_for_transaction = Mock(side_effect=Exception("Transaction failed"))

        # Assert that a ValidationError is raised with the correct message
        with self.assertRaises(ValidationError) as context:
            self.account_service.deposit_savings(valid_savings_account.account_id, 100.0)

        self.assertEqual(str(context.exception), "Deposit failed: Transaction failed")

        # Verify get_account was called once with the correct account_id
        self.account_service.get_account.assert_called_once_with(valid_savings_account.account_id)

    def test_deposit_savings_success(self):
        valid_savings_account = FakeSavingsAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = uuid4()

        # Mock get_account to return the valid savings account
        self.account_service.get_account = Mock(return_value=valid_savings_account)

        # Mock create_new_transaction to return a transaction object
        self.account_service.validate_accounts_for_transaction = Mock()

        # Call the deposit_savings method
        self.account_service.deposit_savings(valid_savings_account.account_id, 100.0)

        # Verify get_account was called once with the correct account_id
        self.account_service.get_account.assert_called_once_with(valid_savings_account.account_id)

        # Verify validate_accounts_for_transaction was called once with the correct arguments
        self.account_service.validate_accounts_for_transaction.assert_called_once_with(100.0, valid_savings_account.reference_account_id, valid_savings_account.account_id)


    def test_withdraw_savings_negative_amount(self):
        valid_savings_account = FakeCheckingAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(return_value=valid_savings_account)

        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(valid_savings_account.account_id, -100.0)

        self.assertEqual(str(context.exception), "Withdrawal amount must be greater than zero.")

    def test_withdraw_savings_no_savings_account(self):
        valid_savings_account = FakeCheckingAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0

        self.account_service.get_account = Mock(return_value=None)

        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(valid_savings_account.account_id, 100.0)

        self.assertEqual(str(context.exception), f"Savings account with ID {valid_savings_account.account_id} does not exist.")

    def test_withdraw_savings_no_reference_account_id(self):
        valid_savings_account = FakeCheckingAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = None

        self.account_service.get_account = Mock(return_value=valid_savings_account)

        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(valid_savings_account.account_id, 100.0)

        self.assertEqual(str(context.exception), f"Account with ID {valid_savings_account.reference_account_id} does not exist.")

    def test_withdraw_savings_insufficient_funds(self):
        valid_savings_account = FakeSavingsAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = uuid4()

        # Mock get_account to return the valid savings account
        self.account_service.get_account = Mock(return_value=valid_savings_account)

        # Mock get_balance to return a balance less than the withdrawal amount
        self.account_service.get_balance = Mock(return_value=500.0)

        # Assert that a ValidationError is raised with the correct message
        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(valid_savings_account.account_id, 1000.0)

        self.assertEqual(str(context.exception), "Withdrawal failed: Withdrawal amount (1000.0) exceeds balance.")

        # Verify get_account was called once with the correct account_id
        self.account_service.get_account.assert_called_once_with(valid_savings_account.account_id)

    def test_withdraw_savings_failure(self):
        valid_savings_account = FakeSavingsAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = uuid4()

        # Mock get_account to return the valid savings account
        self.account_service.get_account = Mock(return_value=valid_savings_account)

        # Mock get_balance to return a balance greater than the withdrawal amount
        self.account_service.get_balance = Mock(return_value=1000.0)

        # Mock create_new_transaction to raise an exception
        self.transaction_service.create_new_transaction = Mock(side_effect=Exception("Transaction failed"))

        # Assert that a ValidationError is raised with the correct message
        with self.assertRaises(ValidationError) as context:
            self.account_service.withdraw_savings(valid_savings_account.account_id, 100.0)

        self.assertEqual(str(context.exception), "Withdrawal failed: Transaction failed")

        # Verify get_account was called once with the correct account_id
        self.account_service.get_account.assert_called_once_with(valid_savings_account.account_id)

    def test_withdraw_savings_success(self):
        valid_savings_account = FakeSavingsAccount()
        valid_savings_account.account_id = uuid4()
        valid_savings_account.opening_balance = 1000.0
        valid_savings_account.reference_account_id = uuid4()

        # Mock get_account to return the valid savings account
        self.account_service.get_account = Mock(return_value=valid_savings_account)

        # Mock get_balance to return a balance greater than the withdrawal amount
        self.account_service.get_balance = Mock(return_value=1000.0)

        # Mock create_new_transaction to raise an exception
        self.transaction_service.create_new_transaction = Mock(return_value=True)

        # Call the withdraw_savings method
        self.account_service.withdraw_savings(valid_savings_account.account_id, 100.0)

        # Verify get_account was called once with the correct account_id
        self.account_service.get_account.assert_called_once_with(valid_savings_account.account_id)

    def test_validate_account_for_atm_no_account(self):

        # Mock that account_sercice.get_account returns None
        self.account_service.get_account = Mock(return_value=None)

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_account_for_atm(10, uuid4(), 20)

        self.assertEqual(str(context.exception), "Account not found.")


    def test_validate_account_for_atm_invalid_pin(self):

        mock_account = self.account_one
        mock_account.PIN = "1234"

        self.account_service.get_account = Mock(return_value=mock_account)


        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_account_for_atm(10, mock_account.account_id, "2012")

        self.assertEqual(str(context.exception), "Invalid PIN.")

    def test_validate_account_for_atm_not_checking_account(self):

        mock_account = self.account_two
        mock_account.PIN = "1234"

        self.account_service.get_account = Mock(return_value=mock_account)

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_account_for_atm(10, mock_account.account_id, "1234")

        self.assertEqual(str(context.exception), f"ATM transactions are allowed only for checking accounts.")


    def test_validate_account_for_atm_overdraft_limit(self):

        mock_account = self.account_one
        mock_account.PIN = "1234"

        self.account_service.get_account = Mock(return_value=mock_account)
        self.account_service.get_balance = Mock(return_value=-1000.0)

        with self.assertRaises(ValidationError) as context:
            self.account_service.validate_account_for_atm(2000, mock_account.account_id, "1234")

        self.assertEqual(str(context.exception), "Overdraft limit (1000.0) overreached")

    def test_validate_account_for_atm_success(self):

        mock_account = self.account_one
        mock_account.PIN = "1234"

        self.account_service.get_account = Mock(return_value=mock_account)
        self.account_service.get_balance = Mock(return_value=1000.0)

        result = self.account_service.validate_account_for_atm(200, mock_account.account_id, "1234")

        self.assertTrue(result)

    def tearDown(self):
        patch.stopall()


