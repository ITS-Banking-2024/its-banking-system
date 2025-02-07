from typing import Optional, Union
from uuid import UUID

from django.db.models import QuerySet, Manager

from accounts.models import Account


class AccountManager(Manager):

    def get_by_account_id(self, account_id: UUID) -> Optional[Account]:
        # Query for Account object by account_id (UUID)
        qs = self.get_queryset().filter(account_id=account_id)
        return qs.first() if qs.exists() else None

    def get_by_customer_id(self, customer_id: Union[int, str]) -> QuerySet:
    # Query for all Account objects by customer_id (UUID or int)
        return self.get_queryset().filter(customer_id=customer_id)

    def delete_checking_account(self, account_id: str) -> None:
        # Delete a CheckingAccount object by account_id (UUID)
        self.get_queryset().filter(account_id=account_id).delete()