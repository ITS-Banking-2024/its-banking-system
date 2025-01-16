from unittest import TestCase
from unittest.mock import patch, Mock
from customers.services import CustomerService

"""
Please note, that we are inheriting from TestCase form the unittest module and not from django.test.TestCase.
This is because we are not testing any Django specific functionality, but only the service class.
"""


class TestCustomerService(TestCase):
    """
    The setUp method is a special method in the TestCase class of the unittest module that is called
    before each test method in the test case.
    Its purpose is to set up any resources or objects that the test methods will need.
    """

    def setUp(self):
        # Create a mock instance of the Customer model
        self.account_service = Mock()

        # Create an instance of the CustomerService class
        self.customer_service = CustomerService(self.account_service)

    @patch("customers.services.Customer.objects.get")
    def test_get_by_id(self, mock_get):

        # Create a mock instance of the Customer model
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.username = "test_user"

        # Configure the mock Customer.objects.get to return the mock_customer
        mock_get.return_value = mock_customer

        # Use the service to get the customer by ID
        result = self.customer_service.get_by_id(1)

        # Assert that the result matches the mock_customer
        self.assertEqual(result, mock_customer)

        # Assert that Customer.objects.get was called with the correct argument
        mock_get.assert_called_once_with(id=1)

    @patch("customers.services.Customer.objects.get")
    def test_get_by_username(self, mock_get):


        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.username = "test_user"

        mock_get.return_value = mock_customer

        result = self.customer_service.get_by_username("test_user")

        self.assertEqual(result, mock_customer)

        mock_get.assert_called_once_with(username="test_user")

    @patch("customers.services.Customer.objects.get")
    def test_get_customer_accounts_with_one_account(self, mock_get):
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.username = "test_user"

        mock_get.return_value = mock_customer

        # Create a mock account
        mock_account = Mock()

        # Configure the mock account_service to return the mock_account
        self.account_service.get_accounts_by_customer_id.return_value = [mock_account]

        # Use the service to get the customer accounts
        result = self.customer_service.get_customer_accounts(1)

        # Assert that the result matches the mock_account
        self.assertEqual(result, [mock_account])

        # Assert that the account_service.get_accounts_by_customer_id was called with the correct argument
        self.account_service.get_accounts_by_customer_id.assert_called_once_with(1)

        self.assertEqual(len(result), 1)

    @patch("customers.services.Customer.objects.get")
    def test_get_customer_accounts_with_multiple_accounts(self, mock_get):
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.username = "test_user"

        mock_get.return_value = mock_customer

        mock_account_one = Mock()
        mock_account_two = Mock()

        self.account_service.get_accounts_by_customer_id.return_value = [mock_account_one, mock_account_two]

        result = self.customer_service.get_customer_accounts(1)

        self.assertEqual(result, [mock_account_one, mock_account_two])

        self.account_service.get_accounts_by_customer_id.assert_called_once_with(1)

        self.assertEqual(len(result), 2)

