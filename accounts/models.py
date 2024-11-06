from django.db import models

from core.models import Account
from accounts.settings import CUSTOMER_MODEL


class AccountBase(Account):

    user_id = models.ForeignKey(CUSTOMER_MODEL, related_name='accounts', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        # swappable is used to be able to change the product model
        swappable: str = "ACCOUNT_MODEL"
        db_table: str = "account_base"

    def __str__(self):
        return f"Account {self.account_id} with balance {self.balance}"

class CheckingAccount(AccountBase):
    class Meta:
        db_table: str = "account_checking"

    is_overdraft_allowed = models.BooleanField(default=True)


class SavingsAccount(AccountBase):
    class Meta:
        db_table: str = "account_savings"

    reference_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE)


class CustodyAccount(AccountBase):
    class Meta:
        db_table: str = "account_custody"

    reference_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE)

