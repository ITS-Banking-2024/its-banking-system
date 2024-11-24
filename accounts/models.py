from django.db import models

from core.models import Account
from accounts.managers import AccountManager
from accounts.settings import CUSTOMER_MODEL


class AccountBase(Account):

    objects : AccountManager = AccountManager()

    customer_id = models.ForeignKey(CUSTOMER_MODEL, related_name='accounts', on_delete=models.CASCADE, null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    type : str = models.CharField(max_length=50, null=False, default='checking', choices=[('checking', 'Checking'), ('savings', 'Savings'), ('custody', 'Custody')])

    class Meta:
        # swappable is used to be able to change the product model
        swappable: str = "ACCOUNT_MODEL"
        db_table: str = "account_base"

    def __str__(self):
        return f"Account {self.account_id}"

class CheckingAccount(AccountBase):
    class Meta:
        db_table: str = "account_checking"

    PIN : str = models.CharField(max_length=4, null=False)


class SavingsAccount(AccountBase):
    class Meta:
        db_table: str = "account_savings"

    reference_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE)


class CustodyAccount(AccountBase):
    class Meta:
        db_table: str = "account_custody"

    reference_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE)

