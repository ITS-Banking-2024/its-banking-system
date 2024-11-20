from unittest.mock import patch
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase
from uuid import uuid4

from unittest.mock import MagicMock

from core.models import Account
from swd_django_demo.settings import CUSTOMER_MODEL
from core.services import IAccountService
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

class DashboardTests(TestCase):

    def setUp(self):
        # Create UUIDs for accounts and customer
        account_id_1 = uuid4()
        account_id_2 = uuid4()
        customer_id = uuid4()

        self.mock_account_list = [
            TestContainer.account_factory(account_id=account_id_1, account_type="checking", user_id=customer_id),
            TestContainer.account_factory(account_id=account_id_2, account_type="savings", user_id=customer_id),
        ]

        # Create an instance of the test container
        self.container = TestContainer()

        # Retrieve the actual service instance from the Singleton provider
        account_service = self.container.account_service()

        # Mock the `get_customer_accounts` method
        account_service.get_accounts_by_customer_id.return_value = self.mock_account_list

        # Wire the view to use the TestContainer dependencies
        self.container.wire(modules=["customers.views"])

        # Create a test user
        User = apps.get_model(CUSTOMER_MODEL)
        self.customer = User.objects.create_user(username="testuser", password="testpassword", email="email@email.com")
        self.customer.customer_id = customer_id

        # Log in the user using the test client
        self.client.login(username="testuser", password="testpassword")

    def test_dashboard(self):

        # Simulate a GET request to the dashboard view
        response = self.client.get(reverse("customers:dashboard"))

        # Assert that the response is 302 -> redirecting to login if not authenticated
        self.assertEqual(response.status_code, 302)

         # Assert that the redirect location is the login page
        self.assertRedirects(response, f"{reverse('customers:customers_login')}?next={reverse('customers:dashboard')}")

    def test_dashboard_authenticated(self):
        # Mock the authenticated user
        with patch("django.contrib.auth.get_user", return_value=self.customer):
            # Simulate a GET request
            response = self.client.get(reverse("customers:dashboard"))

            # Verify status code and template
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "customers/dashboard.html")

            # Verify context contains the expected accounts
            context_accounts = response.context["customer_accounts"]

            for mock_account, context_account in zip(self.mock_account_list, context_accounts):
                # Assert account IDs are the same
                self.assertEqual(mock_account.account_id, context_account.account_id)

                # Assert account balances are the same
                self.assertEqual(mock_account.balance, context_account.balance)

                # Assert account types are the same
                self.assertEqual(mock_account.account_type, context_account.account_type)

                # Assert account user IDs are the same
                self.assertEqual(mock_account.user_id, context_account.user_id)
