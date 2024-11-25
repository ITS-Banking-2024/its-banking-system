from decimal import Decimal
from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from django.db import models
from marshmallow import ValidationError

from accounts.models import AccountBase, CheckingAccount, SavingsAccount, CustodyAccount
from core.models import Account
from core.services import IAccountService


# Concrete implementation of the IAccountService
class AccountService(IAccountService):

    @inject
    def __init__(self, transaction_service: Provide["transaction_service"]):
        self.transaction_service = transaction_service

    def get_account(self, account_id: UUID):
        account = (
                CheckingAccount.objects.filter(account_id=account_id).first()
                or SavingsAccount.objects.filter(account_id=account_id).first()
                or CustodyAccount.objects.filter(account_id=account_id).first()
        )
        return account

    def get_all_accounts(self) -> List[Account]:
        return AccountBase.objects.all()

    def get_accounts_by_customer_id(self, customer_id: UUID) -> models.QuerySet:
        return list(AccountBase.objects.filter(customer_id=customer_id))

    def get_balance(self, account_id: UUID) -> Decimal:
        # Fetch opening_balance as Decimal
        opening_balance = AccountBase.objects.filter(account_id=account_id).first().opening_balance
        balance = Decimal(opening_balance)

        # Fetch transaction history and calculate the balance
        transactions = self.transaction_service.get_transaction_history(account_id, "all_time")
        for transaction in transactions:
            if transaction["sending_account_id"] == str(account_id):
                balance -= Decimal(transaction["amount"])
            elif transaction["receiving_account_id"] == str(account_id):
                balance += Decimal(transaction["amount"])
            else:
                raise ValidationError(f"Transaction not made with this account")

        return balance.quantize(Decimal("0.01"))  # Round to 2 decimal places

    def get_account_totals(self, account_id: UUID, timeframe: str) -> dict:
        total_received = Decimal("0.00")
        total_sent = Decimal("0.00")

        transaction_history = self.transaction_service.get_transaction_history(account_id, timeframe)

        # Calculate total sent and received amounts
        for transaction in transaction_history:
            if str(transaction["sending_account_id"]) == str(account_id):
                total_sent += Decimal(transaction["amount"])
            elif str(transaction["receiving_account_id"]) == str(account_id):
                total_received += Decimal(transaction["amount"])
            else:
                raise ValidationError(f"Rogue transaction.")

        # Round totals to 2 decimal places
        total_sent = total_sent.quantize(Decimal("0.01"))
        total_received = total_received.quantize(Decimal("0.01"))

        return {"total_sent": total_sent, "total_received": total_received}

    def validate_accounts_for_transaction(self, amount: Decimal, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        # Validate sending account
        sending_account = AccountBase.objects.filter(account_id=sending_account_id).first()
        if not sending_account:
            raise ValidationError(f"Sending account with ID {sending_account_id} does not exist.")

        # Validate receiving account
        receiving_account = AccountBase.objects.filter(account_id=receiving_account_id).first()
        if not receiving_account:
            raise ValidationError(f"Receiving account with ID {receiving_account_id} does not exist.")

        # Validate the transaction amount
        if amount <= Decimal(0):
            raise ValidationError("Transaction amount must be greater than zero.")

        return True
