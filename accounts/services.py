from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from django.db import models
from marshmallow import ValidationError

from accounts.managers import AccountManager
from core.services import IAccountService
from accounts.models import AccountBase

from core.models import Account

# this is the concrete impelementation of the IAccountService
class AccountService(IAccountService):

    @inject
    def __init__(self, transaction_service: Provide("transaction_service")):
        self.transaction_service = transaction_service

    def get_balance(self, account_id: UUID,) -> float:
        opening_balance = AccountBase.objects.filter(account_id=account_id).first().opening_balance
        balance = opening_balance
        transactions = self.transaction_service.get_transaction_history(account_id, "all_time")
        for transaction in transactions:
            if transaction["sending_account_id"] == str(account_id):
                balance -= transaction["amount"]
            elif transaction["receiving_account_id"] == str(account_id):
                balance += transaction["amount"]
            else:
                raise ValidationError(f"Transaction not made with this account")
        return balance

    def validate_accounts_for_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        # Validate sending account
        sending_account = AccountBase.objects.filter(account_id=sending_account_id).first()
        if not sending_account:
            raise ValidationError(f"Sending account with ID {sending_account_id} does not exist.")

        # Validate receiving account
        receiving_account = AccountBase.objects.filter(account_id=receiving_account_id).first()
        if not receiving_account:
            raise ValidationError(f"Receiving account with ID {receiving_account_id} does not exist.")

        # Validate the transaction amount
        if amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")

        # Validate sufficient balance in the sending account
        #TODO implement calculate balance using transaction history and opening balance
        #if sending_account.balance < amount:
        #    raise ValidationError("Insufficient balance in the sending account.")
        return True

    def get_all_accounts(self) -> List[Account]:
        return AccountBase.objects.all()


    def get_accounts_by_customer_id(self, customer_id: UUID) -> models.QuerySet:
        return list(AccountBase.objects.filter(customer_id=customer_id))

