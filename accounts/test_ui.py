from unittest.mock import patch
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase
from uuid import uuid4
from django.core.exceptions import ValidationError

from unittest.mock import MagicMock

from core.models import Account
from core.services import IAccountService, ITransactionService
from django.apps import apps


class TestContainer(containers.DeclarativeContainer):
    account_service = providers.Singleton(
        MagicMock,
        spec=IAccountService
    )

    account_factory = providers.Factory(
        MagicMock,
        spec=Account
    )

    transaction_service = providers.Singleton(
        MagicMock,
        spec=ITransactionService
    )


class AccountViewsTest(TestCase):

    def setUp(self):
        self.account_id = uuid4()
        self.customer_id = uuid4()
        self.another_account_id = uuid4()
        self.receiving_account_id = uuid4()

        self.mock_account = TestContainer.account_factory(
            account_id=self.account_id, type="checking", balance=1000, customer_id=self.customer_id, reference_account_id=self.another_account_id)

        # Wire the container and configure the service mocks
        c = TestContainer()

        # Mock `get_account` to return the mock account or None
        def mock_get_account(account_id):
            if account_id == self.account_id:
                return self.mock_account
            return None

        c.account_service().get_account.side_effect = mock_get_account
        c.account_service().get_balance.return_value = 1000
        c.account_service().validate_accounts_for_transaction.return_value = True

        # Mock transaction service behavior
        c.transaction_service().get_transaction_history.return_value = []
        c.transaction_service().create_new_transaction.return_value = None

        # Mock account totals
        self.mock_totals = {"total_received": 0, "total_sent": 0}
        c.account_service().get_account_totals.return_value = self.mock_totals

        c.wire(modules=["accounts.views"])

        self.container = c

    def test_account_detail_success(self):
        response = self.client.get(reverse("accounts:account_detail", args=[self.account_id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/account_details.html")
        self.assertIn("account", response.context)
        self.assertIn("balance", response.context)
        self.assertEqual(response.context["account"], self.mock_account)
        self.assertEqual(response.context["balance"], 1000)

    def test_account_detail_failure(self):
        response = self.client.get(reverse("accounts:account_detail", args=[self.another_account_id]))
        self.assertEqual(response.status_code, 404)

    def test_account_history_no_transactions(self):
        response = self.client.get(reverse("accounts:history", args=[self.account_id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/transaction_history.html")

        self.assertIn("account", response.context)
        self.assertIn("transaction_history", response.context)
        self.assertIn("selected_timeframe", response.context)
        self.assertIn("total_received", response.context)
        self.assertIn("total_sent", response.context)

        self.assertEqual(response.context["account"], self.mock_account)
        self.assertEqual(response.context["transaction_history"], [])
        self.assertEqual(response.context["total_received"], 0)
        self.assertEqual(response.context["total_sent"], 0)
        self.assertEqual(response.context["selected_timeframe"], "all_time")

    def test_account_history_no_transactions(self):
        response = self.client.get(reverse("accounts:history", args=[self.account_id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/transaction_history.html")

        self.assertIn("account", response.context)
        self.assertIn("transaction_history", response.context)
        self.assertIn("selected_timeframe", response.context)
        self.assertIn("total_received", response.context)
        self.assertIn("total_sent", response.context)

        self.assertEqual(response.context["account"], self.mock_account)
        self.assertEqual(response.context["transaction_history"], [])
        self.assertEqual(response.context["total_received"], 0)
        self.assertEqual(response.context["total_sent"], 0)
        self.assertEqual(response.context["selected_timeframe"], "all_time")

    def test_new_transaction_get_request(self):
        response = self.client.get(reverse("accounts:new_transaction", args=[self.account_id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/new_transaction.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["account_id"], self.account_id)


    def test_new_transaction_post_validation_error(self):
        self.container.account_service().validate_accounts_for_transaction.return_value = False

        form_data = {"receiving_account_id": self.receiving_account_id, "amount": 500}
        response = self.client.post(reverse("accounts:new_transaction", args=[self.account_id]), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/success_screen.html")

        self.assertFalse(response.context["success"])
        self.assertEqual(response.context["message"], "Accounts validation failed.")
        self.assertEqual(response.context["account_id"], self.account_id)

        self.container.account_service().validate_accounts_for_transaction.assert_called_once_with(
            500, self.account_id, self.receiving_account_id
        )
        self.container.transaction_service().create_new_transaction.assert_not_called()

    def test_new_transaction_post_success(self):
        form_data = {"receiving_account_id": self.receiving_account_id, "amount": 500}
        response = self.client.post(reverse("accounts:new_transaction", args=[self.account_id]), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/success_screen.html")

        self.assertTrue(response.context["success"])
        self.assertEqual(response.context["message"], "Transaction created successfully!")
        self.assertEqual(response.context["account_id"], self.account_id)

        self.container.account_service().validate_accounts_for_transaction.assert_called_once_with(
            500, self.account_id, self.receiving_account_id
        )
        self.container.transaction_service().create_new_transaction.assert_called_once_with(
            500, self.account_id, self.receiving_account_id
        )

    def test_new_transaction_post_general_failure(self):

        self.container.account_service().validate_accounts_for_transaction.return_value = True
        self.container.transaction_service().create_new_transaction.side_effect = ValidationError("Error")

        with self.assertRaises(ValidationError) as context:
            form_data = {"receiving_account_id": self.receiving_account_id, "amount": 500}
            self.client.post(reverse("accounts:new_transaction", args=[self.account_id]), data=form_data)


        self.assertEqual(context.exception.messages, ["Error"])

    def test_savings_get_request(self):
        # Mock the balance
        self.container.account_service().get_balance.return_value = 1000

        # Simulate a GET request
        response = self.client.get(reverse("accounts:savings", args=[self.account_id]))

        # Verify response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/savings_transaction.html")

        # Verify the context contains the correct account ID and balance
        self.assertEqual(response.context["account_id"], self.account_id)
        self.assertEqual(response.context["balance"], 1000)
        self.assertIn("form", response.context)

    def test_savings_post_deposit_success(self):
        # Simulate a successful deposit transaction
        form_data = {"transaction_type": "deposit", "amount": 500}
        response = self.client.post(reverse("accounts:savings", args=[self.account_id]), data=form_data)

        # Verify the response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/success_screen.html")

        # Verify the success message
        self.assertTrue(response.context["success"])
        self.assertEqual(response.context["message"], "Deposit successful!")
        self.assertEqual(response.context["account_id"], self.account_id)

        # Verify the deposit method was called
        self.container.account_service().deposit_savings.assert_called_once_with(self.account_id, 500)

    def test_savings_post_withdraw_success(self):
        # Simulate a successful withdrawal transaction
        form_data = {"transaction_type": "withdraw", "amount": 300}
        response = self.client.post(reverse("accounts:savings", args=[self.account_id]), data=form_data)

        # Verify the response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/success_screen.html")

        # Verify the success message
        self.assertTrue(response.context["success"])
        self.assertEqual(response.context["message"], "Withdraw successful!")
        self.assertEqual(response.context["account_id"], self.account_id)

        # Verify the withdraw method was called
        self.container.account_service().withdraw_savings.assert_called_once_with(self.account_id, 300)

    def test_savings_post_invalid_transaction_type_raises_error(self):
            # Simulate a POST request with an invalid transaction type
            form_data = {"transaction_type": "invalid", "amount": 500}

            # Make the POST request
            response = self.client.post(reverse("accounts:savings", args=[self.account_id]), data=form_data)

            # Verify the response status code
            self.assertEqual(response.status_code, 200)
            self.assertRaises(ValidationError)

            # Verify the correct template is used
            self.assertTemplateUsed(response, "accounts/savings_transaction.html")

            # Ensure the service methods were not called
            self.container.account_service().deposit_savings.assert_not_called()
            self.container.account_service().withdraw_savings.assert_not_called()