# this can be seen as our repository for our model
from typing import Optional, List

from core.managers import CoreProductManager
from products.models import Product


class ProductManager(CoreProductManager):
    def get_by_id(self, id: int) -> Optional[Product]:
        # Query for Product object by id
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_name(self, name: str) -> List[Product]:
        # Query for Product objects by name
        return self.get_queryset().filter(name=name)

    def get_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        # Query for Product objects by price range
        return self.get_queryset().filter(price__gte=min_price, price__lte=max_price)
