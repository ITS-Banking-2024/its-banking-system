from django.db import models

# Create your models here.
from core.models import Product
from products.managers import ProductManager


class ProductBase(Product):
    class Meta:
        # swappable is used to be able to change the product model
        swappable: str = "PRODUCT_MODEL"
        db_table: str = "products_base"


# this is the concrete model that we will use for the project
class Product(ProductBase):
    objects: ProductManager = ProductManager()

    class Meta:
        db_table: str = "products_simple"

    # we are adding a price field to the product model
    price: float = models.FloatField()
