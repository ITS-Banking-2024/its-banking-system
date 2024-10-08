# this can be seen as our repository for our model
from django.db import models

"""
The OrderManager class is a custom manager for the Order model.
It provides a method to retrieve an order by its ID.
"""


class OrderManager(models.Manager):
    # This method retrieves an order by its ID
    def get_by_id(self, id: int) -> models.QuerySet:
        # First, we get the queryset for all orders with the given ID
        qs: models.QuerySet = self.get_queryset().filter(id=id)
        # If there is exactly one order with the given ID, return it
        if qs.count() == 1:
            return qs.first()
        return None
