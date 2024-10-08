import unittest
from unittest.mock import Mock, patch

from orders.services import OrderService


class TestOrderService(unittest.TestCase):
    """
     The setUp method is a special method in the TestCase class of the unittest module that is called
     before each test method in the test case.
     Its purpose is to set up any resources or objects that the test methods will need.
     """

    def setUp(self):
        # create a mock instance of customer_service and product_service
        self.customer_service = Mock()
        self.product_service = Mock()
        # create a real OrderService instance and provide the mock instances
        self.order_service = OrderService(self.product_service, self.customer_service)

        # we patch the Order model in the orders.services module to isolate the test from the database
        # you always have to patch WHERE the object is USED, not where it is defined
        self.mock_order_model = patch('orders.services.Order').start()
        self.mock_order_model_position = patch('orders.services.OrderPosition').start()

        # Sample data for order creation.
        self.data = {
            'customer': {'username': 'sample_user'},
            'order_positions': [
                {'product': {'id': 1}, 'quantity': 2, 'price': 10.0},
                {'product': {'id': 2}, 'quantity': 3, 'price': 15.0},
            ]
        }

    """
    The tearDown method is a special method in the TestCase class of the unittest module that is called
    after each test method in the test case.
    """

    def tearDown(self):
        patch.stopall()

    def test_create_order_customer_has_credit(self):
        # Set the redeem_credit method of the mock instance to return True
        self.customer_service.redeem_credit.return_value = True
        order = self.order_service.make_order_from_dto(self.data)
        assert order is not None  # assert that the order is not None
        assert order.save.called  # assert that the save method of the order was called
        assert self.customer_service.redeem_credit.called  # assert that the redeem_credit method was called

    def test_create_order_customer_without_credit(self):
        # Set the redeem_credit method of the mock instance to return True
        self.customer_service.redeem_credit.return_value = False
        with self.assertRaises(Exception):
            self.order_service.make_order_from_dto(self.data)
        assert self.customer_service.redeem_credit.called


