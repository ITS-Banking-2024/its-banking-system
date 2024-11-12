from django.test import TestCase
from customers.models import Customer

class TestCustomer(TestCase):
    def setUp(self) -> None:
        pass

    def test_new_customer(self) -> None:
        # Create a Customer instance
        customer = Customer.objects.create(
            username="testuser",
            credit=1000.00
        )

        # Verify that the Customer instance was created and can be retrieved
        retrieved_customer = Customer.objects.get_by_user_id(customer.user_id)
        self.assertIsNotNone(retrieved_customer)
        self.assertEqual(retrieved_customer.user_id, customer.user_id)

    def test_delete_customer(self) -> None:
        # Create a Customer instance
        customer = Customer.objects.create(
            username="testuser",
            credit=1000.00
        )

        # Verify that the Customer instance was created and can be retrieved
        retrieved_customer = Customer.objects.get_by_user_id(customer.user_id)
        self.assertIsNotNone(retrieved_customer)

        # Delete the Customer instance
        Customer.objects.delete_customer(customer.user_id)

        # Verify that the Customer instance was deleted
        retrieved_customer = Customer.objects.get_by_user_id(customer.user_id)
        self.assertIsNone(retrieved_customer)

    def test_get_all_customers(self) -> None:
        # Create a Customer instance
        customer_1 = Customer.objects.create(
            username="testuser",
            credit=1000.00
        )

        customer_2 = Customer.objects.create(
            username="testuser2",
            credit=2000.00
        )

        all_customers = Customer.objects.get_all_customers()
        self.assertEqual(len(all_customers), 2)