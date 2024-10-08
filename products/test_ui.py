from unittest.mock import MagicMock

from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase

from core.models import Product
from core.services import IProductService

"""
    This is a test container that we will be used to mock the dependencies,
    as we don't want to test the dependencies, but ONLY the view itself.
"""


class TestContainer(containers.DeclarativeContainer):
    product_factory = providers.Factory(
        MagicMock,
        spec=Product
    )

    product_service = providers.Singleton(
        MagicMock,
        spec=IProductService
    )


# This test class inherits from the TestCase class, which is provided by Django (not form unittest),
# as it provides some additional functionality that we need for testing Django views
class IndexTests(TestCase):
    """
    The setUp method is a special method in the TestCase class of the unittest module that is called
    before each test method in the test case.
    Its purpose is to set up any resources or objects that the test methods will need.
    """
    def setUp(self):
        # Create a list of mock products
        # We are using the factory provider to create mock products and are not using a concrete product implementation
        self.mock_product_list = [
            TestContainer.product_factory(id=1, name="testproduct1", description="testdescription1"),
            TestContainer.product_factory(id=2, name="testproduct2", description="testdescription2"),
        ]
        # Create an instance of the test container
        c = TestContainer()
        # Set the return value of the get_all_products method of the mock product service
        # so we do not use a concrete product service, but a mock, for the service we have our own unit tests
        c.product_service().get_all_products.return_value = self.mock_product_list
        # Wire the modules to use the TestContainer for the dependencies
        c.wire(modules=["products.views", ])

    def test_index(self):
        response = self.client.get(reverse("products:index"))

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # check that the correct template was used
        self.assertTemplateUsed(response, "products/index.html")
        # Check that the rendered context contains the list of products
        self.assertIn('products_list', response.context)
        self.assertEqual(list(response.context['products_list']), self.mock_product_list)
