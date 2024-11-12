from typing import List

from django.db import models

from core.services import IAccountService
from accounts.models import Account, CheckingAccount, SavingsAccount, CustodyAccount

# this is the concrete impelementation of the IAccountService
class AccountService(IAccountService):

    def get_all_accounts(self) -> List[Account]:
        return Account.objects.all()

    def get_account_balance(self, account: Account) -> float:
        return account.balance

    def get_by_id(self, id: int) -> models.QuerySet:
        try:
            return Account.objects.get(id=id)
        except Account.DoesNotExist:
            return None