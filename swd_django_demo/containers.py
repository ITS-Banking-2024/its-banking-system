"""
In this file, a Container class is defined that uses dependency_injector to manage the dependencies of the application.
The container declares three dependencies: config, product_service, and order_service.
config is a configuration provider, while product_service and order_service are singletons that provide instances
of ProductService and OrderService, respectively.
Additionally, a product_factory is defined as a factory provider that creates instances of the Product model.
"""

from dependency_injector import containers, providers

from customers.services import CustomerService
from orders.services import OrderService
from products.models import Product
from products.services import ProductService
from transactions.services import BankingServiceImpl, TradingServiceImpl



# define a container class and declare its dependencies
class Container(containers.DeclarativeContainer):
    # configuration provider
    config = providers.Configuration()

    # Singleton provider for ProductService
    product_service = providers.Singleton(
        ProductService,
    )

    customer_service = providers.Singleton(
        CustomerService,
    )

    # Factory provider for creating instances of Product model
    product_factory = providers.Factory(Product, id=int, name=str, description=str )

    # Singleton provider for OrderService with product_service as a dependency
    order_service = providers.Singleton(
        OrderService, product_service=product_service, customer_service=customer_service
    )

    banking_service = providers.Singleton(
        BankingServiceImpl,
    )

    trading_service = providers.Singleton(
        TradingServiceImpl,
    )