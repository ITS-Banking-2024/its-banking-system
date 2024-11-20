import logging
from typing import List, Optional
from .logging import logger

from dependency_injector.wiring import inject, Provide
from django.db import transaction

from core.serializers import CustomerSerializer
from orders.dtos import OrderDTO, OrderPositionDTO, ProductSerializer
from orders.models import Order, OrderPosition

"""
Please note, that we are only importing the interfaces from the core module and not the concrete classes.
So this module can be used with any concrete product module implementation.
"""
from core.models import Product, Customer
from core.services import IOrderService


class OrderService(IOrderService):
    """
     A class that implements IOrderService interface to handle order related business logic.
     """

    # inject decorator is used to inject dependencies into the constructor method.
    @inject
    def __init__(self, product_service: Provide("product_service"), customer_service: Provide("customer_service")):
        logger.debug(f"OrderService.__init__(product_service: {product_service}, customer_service: {customer_service}")
        """
        Constructor method to initialize OrderService class.
        Args:
            product_service (Provide["product_service"]): An injected dependency to access the ProductService class.
                Provide("product_service") is a special constant value provided by the dependency_injector library that
                can be used as a placeholder when injecting dependencies.
                It indicates that the value for the argument should be provided by the dependency injection
                framework at runtime, rather than being explicitly passed in at the time of object creation.
        """
        self.product_service = product_service
        self.customer_service = customer_service

    def get_all_products(self) -> List[Product]:
        logger.debug(f"OrderService.get_all_products()")
        return self.product_service.get_all_products()

    def get_product(self, product_id: int) -> Product:
        logger.debug(f"OrderService.get_product(product_id : {product_id})")
        return self.product_service.get_by_id(product_id)

    def get_order_dto(self, customer: Customer, product_list: []) -> OrderDTO:
        logger.debug(f"OrderService.get_order_dto(customer: {customer}, product_list: {product_list})")
        order: OrderDTO = OrderDTO()
        order.customer = CustomerSerializer().dump(customer)
        order_positions: [] = []  # List to store the order positions
        product_pos_map: {} = {}  # Map to store the product id and position in the order
        pos: int = 0
        total_price: float = 0.0
        for product_id in product_list:
            if product_id in product_pos_map:
                orderpos: OrderPositionDTO = order_positions[product_pos_map[product_id]]
                orderpos.quantity += 1
                total_price += self.product_service.get_price(self.product_service.get_by_id(product_id))
            else:
                product: Product = self.product_service.get_by_id(product_id)
                if product is None:
                    continue
                product_serialized = ProductSerializer().dump(product)
                pos += 1
                product_pos_map[product_id] = pos - 1
                orderpos: OrderPositionDTO = OrderPositionDTO()
                orderpos.pos=pos
                orderpos.product=product_serialized
                orderpos.quantity=1
                # we need to get the price from the product service, because the abstract product does not have price
                orderpos.price=self.product_service.get_price(product)
                total_price += orderpos.price
                order_positions.append(orderpos)  # Add the order position to the list

        order.order_positions = order_positions
        order.total_price = total_price

        return order

    def create_order(self, order_dto: OrderDTO) -> Optional[int]:
        logger.debug(f"OrderService.create_order(order_dto: {order_dto})")
        # loading the order_dto into the Order model already saves the order and order positions to the database
        # in case of an error, the transaction will be rolled back, so we use the atomic decorator
        # putting everything into an atomic transaction also give us the possibility to handle multiuser concurrency
        try:
            with transaction.atomic():
                # this will call the make_order_from_dto method below,
                # see dtos.py where special conversion method is defined with @post_load()
                order: Order = OrderDTO().load(order_dto)
                return order.id
        except Exception as e:
                print(e)
                return None

    def make_order_from_dto(self, data, **kwargs) -> Order:
        logger.debug(f"OrderService.create_order(data: {data}, kwargs: {kwargs})")
        order_positions = data.pop('order_positions', [])
        customer_data = data.pop('customer', {})
        user_name = customer_data.get('username')
        customer = self.customer_service.get_by_username(user_name)


        order = Order(user=customer, **data)
        order.save();
        for order_position in order_positions:
            product_id = order_position.pop('product', {}).get('id')
            product = self.product_service.get_by_id(product_id)
            order_position = OrderPosition(**order_position, product=product)
            order_position.order = order
            order_position.save()

        return order

