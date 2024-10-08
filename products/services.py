from typing import List

from django.db import models

from core.services import IProductService
from products.models import Product


# this is the concrete implementation of the IProductService
class ProductService(IProductService):

    def get_all_products(self) -> List[Product]:
        return Product.objects.all()

    def get_price(self, product: Product) -> float:
        # in another product app, the logic for getting the price could be different
        return product.price

    def get_by_id(self, id: int) -> models.QuerySet:
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

