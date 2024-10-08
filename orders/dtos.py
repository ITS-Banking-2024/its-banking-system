from dependency_injector.wiring import Provide, inject
from marshmallow import Schema, fields, post_load

from core.serializers import CustomerSerializer, ProductSerializer
from core.services import IOrderService
from orders.models import Order, OrderPosition


# Parallel class representing the Order entity as a DTO The DTO is used to transfer data between the service and the
# controller layer it would not be easy to use the Django model directly in the controller layer, especially when the
# model is complex and when we do not want to save the object already in the database and working with not yet saved
# objects is not easy in Django (e.g. the id is not yet set, so we cannot use it, cannot access foreign key objects, ..)
# (limitations due to the Active Record pattern in Django ORM)

class OrderDTO(Schema):
    # The as_string=True option is used to ensure that the id is serialized as a string to avoid integer overflow
    order_number: fields.Integer = fields.Integer(as_string=True, attribute='id')
    customer: fields.Nested = fields.Nested(CustomerSerializer)
    order_positions: fields.Nested = fields.Nested('OrderPositionDTO', many=True)
    total_price: fields.Float = fields.Float()

    @post_load()
    @inject
    def make_order(self, data, order_service: IOrderService = Provide["order_service"], **kwargs) -> Order:
        return order_service.make_order_from_dto(data, **kwargs)


# Parallel class representing the OrderPosition entity
class OrderPositionDTO(Schema):
    # order = fields.Nested(lambda: OrderDTO)
    pos: fields.Int = fields.Int()
    product: fields.Nested = fields.Nested(ProductSerializer)
    quantity: fields.Int = fields.Int()
    price: fields.Float = fields.Float()

