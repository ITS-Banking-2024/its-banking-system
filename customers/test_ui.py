from unittest.mock import patch
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase
from uuid import uuid4

from unittest.mock import MagicMock

from core.models import Account
from core.services import IAccountService, ICustomerService
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

    customer_service = providers.Singleton(
        MagicMock,
        spec=ICustomerService
        )

class DashboardTests(TestCase):

    def setUp(self):
        self.customer_id = uuid4()

        self.account_id = uuid4()

        self.mock_account_list = [
            {"account_id": uuid4(), "type": "checking", "balance": 1000, "customer_id": self.customer_id},
            {"account_id": uuid4(), "type": "savings", "balance": 2000, "customer_id": self.customer_id}
        ]


        c = TestContainer()
        c.customer_service().get_customer_accounts.return_value = self.mock_account_list
        c.wire(modules=["customers.views"])


        # Mock user
        with patch('django.apps.apps.get_model') as mock_get_model:
            self.mock_user = MagicMock()
            self.mock_user.id = self.customer_id
            self.mock_user.customer_id = self.customer_id
            mock_get_model.return_value.objects.create_user.return_value = self.mock_user

        # Authenticate the mock user
        self.customer = self.mock_user
        self.client.login(username="testuser", password="testpassword")

    def test_dashboard(self):

        # Simulate a GET request to the dashboard view
        response = self.client.get(reverse("customers:dashboard"))

        # Assert that the response is 302 -> redirecting to login if not authenticated
        self.assertEqual(response.status_code, 302)

         # Assert that the redirect location is the login page
        self.assertRedirects(response, f"{reverse('customers:customers_login')}?next={reverse('customers:dashboard')}")

    def test_dashboard_authenticated_no_accounts(self):
        # Mock the authenticated user
        with patch("django.contrib.auth.get_user", return_value=self.mock_user):
            # Simulate a GET request
            response = self.client.get(reverse("customers:dashboard"))

            # Verify status code and template
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "customers/dashboard.html")

    def test_dashboard_authenticated_with_accounts(self):
        # Mock the authenticated user and accounts
        with patch("django.contrib.auth.get_user", return_value=self.mock_user), \
            patch("core.services.ICustomerService.get_customer_accounts", return_value=self.mock_account_list):

            # Simulate a GET request
            response = self.client.get(reverse("customers:dashboard"))

            # Debugging step: print context
            print("Response context:", response.context)

            # Verify status code and template
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "customers/dashboard.html")

            # Verify the context contains user accounts
            context_accounts = response.context.get("customer_accounts", [])
            self.assertEqual(context_accounts, self.mock_account_list)
            self.assertEqual(len(context_accounts), 2)

            # Verify the context data
            self.assertEqual(context_accounts[0]["account_id"], self.mock_account_list[0]["account_id"])
            self.assertEqual(context_accounts[0]["type"], self.mock_account_list[0]["type"])
            self.assertEqual(context_accounts[0]["balance"], self.mock_account_list[0]["balance"])
            self.assertEqual(context_accounts[0]["customer_id"], self.mock_account_list[0]["customer_id"])


            self.assertEqual(context_accounts[1]["account_id"], self.mock_account_list[1]["account_id"])
            self.assertEqual(context_accounts[1]["type"], self.mock_account_list[1]["type"])
            self.assertEqual(context_accounts[1]["balance"], self.mock_account_list[1]["balance"])
            self.assertEqual(context_accounts[1]["customer_id"], self.mock_account_list[1]["customer_id"])
