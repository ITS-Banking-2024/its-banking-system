from typing import List

from core.services import IProductService
from product_alternative.models import Product


class ProductServiceAlternative(IProductService):
    def get_price(self, product: Product) -> float:
        return product.price * 1.2

    def get_all_products(self) -> List[Product]:
        return Product.objects.all();