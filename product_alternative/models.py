from django.db import models

# Create your models here.
from core.models import Product


class ProductBase(Product):
    class Meta:
        swappable: str = "PRODUCT_MODEL"
        db_table: str = "products_base"


class Product(ProductBase):
    class Meta:
        db_table: str = "products_advanced"

    category: str = models.CharField(max_length=100)
