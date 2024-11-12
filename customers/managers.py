from typing import Optional, List, Union
from django.db.models import QuerySet
from core.managers import CoreProductManager
from core.models import Customer

class CustomerManager(CoreProductManager):

    def get_by_user_id(self, user_id: Union[int, str]) -> Optional[Customer]:
        # Query for Customer object by user_id (UUID or int)
        qs = self.get_queryset().filter(user_id=user_id)
        return qs.first() if qs.exists() else None

    def delete_customer(self, user_id: Union[int, str]) -> None:
        # Delete a Customer object by user_id (UUID or int)
        self.get_queryset().filter(user_id=user_id).delete()

    def get_all_customers(self) -> QuerySet:
        # Query for all Customer objects
        return self.get_queryset().all()