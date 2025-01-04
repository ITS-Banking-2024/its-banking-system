from django.db import models

from core.models import Account
from accounts.managers import AccountManager
from accounts.settings import CUSTOMER_MODEL


class AccountBase(Account):

    objects : AccountManager = AccountManager()

    customer_id = models.ForeignKey(CUSTOMER_MODEL, related_name='accounts', on_delete=models.PROTECT, null=True, blank=True)
    type : str = models.CharField(max_length=50, null=False, default='checking', choices=[('checking', 'Checking'), ('savings', 'Savings'), ('custody', 'Custody')])

    class Meta:
        # swappable is used to be able to change the product model
        swappable: str = "ACCOUNT_MODEL"
        db_table: str = "account_base"

    def __str__(self):
        return f"Account {self.account_id}"

class CheckingAccount(AccountBase):
    class Meta:
        db_table = "account_checking"

    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    PIN = models.CharField(max_length=4, null=False)

    def save(self, *args, **kwargs):
        self.type = 'checking'  # Enforce the type value
        super().save(*args, **kwargs)


class SavingsAccount(AccountBase):
    class Meta:
        db_table = "account_savings"

    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reference_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.type = 'savings'  # Enforce the type value
        super().save(*args, **kwargs)


class CustodyAccount(AccountBase):
    class Meta:
        db_table = "account_custody"

    reference_account = models.ForeignKey(CheckingAccount, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.type = 'custody'  # Enforce the type value
        super().save(*args, **kwargs)