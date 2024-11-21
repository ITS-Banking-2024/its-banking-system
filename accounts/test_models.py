from django.test import TestCase
from django.apps import apps
from accounts.models import AccountBase, CheckingAccount, SavingsAccount, CustodyAccount
from accounts.settings import CONCRETE_CUSTOMER_MODEL as CUSTOMER_MODEL

# Create your tests here.


class TestAccounts(TestCase):
    def setUp(self) -> None:

        # Get the Customer model
        Customer = apps.get_model(CUSTOMER_MODEL)

        self.customer = Customer.objects.create(username="testuser")

    def test_new_checking_account(self) -> None:
        # Create a CheckingAccount instance as the reference account
        checking_account = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN = "1234"
        )

        # Verify that the CheckingAccount instance was created and can be retrieved
        retrieved_account = CheckingAccount.objects.get_by_account_id(checking_account.account_id)
        self.assertIsNotNone(retrieved_account)
        self.assertEqual(retrieved_account.account_id, checking_account.account_id)


    def test_new_savings_account(self) -> None:
        # Create a CheckingAccount instance as the reference account
        checking_account = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN = '1234'
        )

        # Create a SavingsAccount instance with the reference account
        savings_account = SavingsAccount.objects.create(
            customer_id=self.customer,
            reference_account=checking_account
        )

        # Verify that the SavingsAccount instance was created and can be retrieved
        retrieved_account = SavingsAccount.objects.get_by_account_id(savings_account.account_id)
        self.assertIsNotNone(retrieved_account)
        self.assertEqual(retrieved_account.account_id, savings_account.account_id)
        self.assertEqual(retrieved_account.reference_account, checking_account)

    def test_new_custody_account(self) -> None:
        # Create a CheckingAccount instance as the reference account
        checking_account = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN = '1234'
        )

        # Create a CustodyAccount instance with the reference account
        custody_account = CustodyAccount.objects.create(
            customer_id=self.customer,
            reference_account=checking_account
        )

        # Verify that the CustodyAccount instance was created and can be retrieved
        retrieved_account = CustodyAccount.objects.get_by_account_id(custody_account.account_id)
        self.assertIsNotNone(retrieved_account)
        self.assertEqual(retrieved_account.account_id, custody_account.account_id)
        self.assertEqual(retrieved_account.reference_account, checking_account)


    def test_find_single_account_by_customer_id(self):
        # Create a CheckingAccount instance for the customer
        checking_account = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN="1234"
        )


        # Retrieve accounts by customer_id
        retrieved_accounts = CheckingAccount.objects.get_by_customer_id(self.customer)

        # Assert that retrieved accounts are not None and contain the created checking_account
        self.assertIsNotNone(retrieved_accounts)
        self.assertIn(checking_account, retrieved_accounts)


    def test_find_all_accounts_by_customer_id(self):
        # Create multiple CheckingAccount instances for the customer
        checking_account_1 = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN = "1234"
        )
        checking_account_2 = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN="2345"
        )

        # Retrieve accounts by customer_id
        retrieved_accounts = CheckingAccount.objects.get_by_customer_id(self.customer)

        # Assert that retrieved accounts are not None and contain the created checking_accounts
        self.assertIsNotNone(retrieved_accounts)
        self.assertIn(checking_account_1, retrieved_accounts)
        self.assertIn(checking_account_2, retrieved_accounts)
        self.assertEqual(len(retrieved_accounts), 2)


    def test_delete_checking_account(self):
        # Create a CheckingAccount instance for the customer
        checking_account = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN = "1234"
        )

        # Delete the checking account
        CheckingAccount.objects.delete_checking_account(checking_account.account_id)

        # Verify that the checking account was deleted
        retrieved_account = CheckingAccount.objects.get_by_account_id(checking_account.account_id)
        self.assertIsNone(retrieved_account)


    def test_deleting_checking_accounts_delete_referenced_account(self):
        # Create a CheckingAccount instance for the customer
        checking_account = CheckingAccount.objects.create(
            customer_id=self.customer,
            PIN="1234"
        )

        # Create a CustodyAccount instance with the reference account
        custody_account = CustodyAccount.objects.create(
            customer_id=self.customer,
            reference_account=checking_account
        )

        # get all accounts from user
        retrieved_accounts = AccountBase.objects.get_by_customer_id(self.customer)

        # Assert that retrieved accounts are not None and contain the created checking_accounts
        self.assertIsNotNone(retrieved_accounts)

        # Delete the checking account
        CheckingAccount.objects.delete_checking_account(checking_account.account_id)

        # Verify that the checking account was deleted
        retrieved_account = CheckingAccount.objects.get_by_account_id(checking_account.account_id)
        self.assertIsNone(retrieved_account)

        # Verify that the custody account was deleted
        retrieved_account = CustodyAccount.objects.get_by_account_id(custody_account.account_id)
        self.assertIsNone(retrieved_account)