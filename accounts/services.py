from typing import List
from uuid import UUID

from django.db import models

from core.services import IAccountService
from accounts.models import AccountBase

from core.models import Account

# this is the concrete impelementation of the IAccountService
class AccountService(IAccountService):

    def get_all_accounts(self) -> List[Account]:
        return AccountBase.objects.all()

    def get_account_balance(self, account: Account) -> float:
        return account.balance

    def get_accounts_by_customer_id(self, customer_id: UUID) -> models.QuerySet:
        return list(AccountBase.objects.filter(user_id=customer_id))


    # implement this method !!!!
    def get_balance(self, account_id):
        return 0

