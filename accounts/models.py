from django.db import models

from core.models import Account

class AccountBase(Account):
    class Meta:
        # swappable is used to be able to change the product model
        swappable: str = "ACCOUNT_MODEL"
        db_table: str = "account_base"

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

