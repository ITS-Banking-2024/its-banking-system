from django.test import TestCase

import swd_django_demo


class TestDependencyContainer(TestCase):

    # this method is called before each test to set up the test environment
    # here we are getting the container from the swd_django_demo package
    def setUp(self):
        self.container = swd_django_demo.get_container()

    def test_product_service(self):
        # fetch the ProductService from the container
        product_service = self.container.product_service();
        # check that product_service is not None
        self.assertIsNotNone(product_service)

    def test_customer_service(self):
        # fetch the CustomerService from the container
        customer_service = self.container.customer_service();
        # check that customer_service is not None
        self.assertIsNotNone(customer_service)

    # def test_order_service(self):
    #     # fetch the OrderService from the container
    #     order_service = self.container.order_service();
    #     # check that order_service is not None
    #     self.assertIsNotNone(order_service)
    #     # check that order_service has a product_service
    #     self.assertIsNotNone(order_service.product_service)
    #     # check that order_service has a customer_service
    #     self.assertIsNotNone(order_service.customer_service)

    # def test_banking_service(self):
    #     transaction_service = self.container.transaction_service();
    #     self.assertIsNotNone(transaction_service)

    # def test_trading_service(self):
    #     trading_service = self.container.trading_service();
    #     self.assertIsNotNone(trading_service)

    # def test_customerImp_service(self):
    #     customerImplService = self.container.customerImpl_service();
    #     self.assertIsNotNone(customerImplService)
    #     self.assertIsNotNone(customerImplService.transaction_service)

    # def test_admin_service(self):
    #     admin_service = self.container.admin_service();
    #     self.assertIsNotNone(admin_service)