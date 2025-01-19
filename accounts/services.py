from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from django.db import transaction
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

    def get_accounts_by_customer_id(self, customer_id: UUID) -> List[Account]:
        return list(AccountBase.objects.filter(customer_id=customer_id))

    def get_bank_custody_account(self):
        try:
            # Fetch using the unique identifier
            bank_custody_account = CustodyAccount.objects.get(unique_identifier="bank_custody_account")
            return bank_custody_account
        except CustodyAccount.DoesNotExist:
            raise ValueError("Bank custody account is not set up. Please check the database configuration.")

    def get_balance(self, account_id: UUID) -> float:
        account = self.get_account(account_id)

        if isinstance(account, CustodyAccount):
            return 0.0
        else:
            opening_balance = account.opening_balance
            balance = float(opening_balance)

            # Fetch transaction history and calculate the balance
            transactions = self.transaction_service.get_transaction_history(account_id, "all_time")
            for single_transaction in transactions:
                if single_transaction["sending_account_id"] == str(account_id):
                    balance -= float(single_transaction["amount"])
                elif single_transaction["receiving_account_id"] == str(account_id):
                    balance += float(single_transaction["amount"])
                else:
                    raise ValidationError(f"Transaction not made with this account")

            return round(balance, 2)

    def get_account_totals(self, account_id: UUID, timeframe: str) -> dict:
        total_received = 0.0
        total_sent = 0.0

        transaction_history = self.transaction_service.get_transaction_history(account_id, timeframe)

        # Calculate total sent and received amounts
        for single_transaction in transaction_history:
            if str(single_transaction["sending_account_id"]) == str(account_id):
                total_sent += float(single_transaction["amount"])
            elif str(single_transaction["receiving_account_id"]) == str(account_id):
                total_received += float(single_transaction["amount"])
            else:
                raise ValidationError(f"Rogue transaction.")

        # Round totals to 2 decimal places
        total_sent = round(total_sent, 2)
        total_received = round(total_received, 2)

        return {"total_sent": total_sent, "total_received": total_received}

    def validate_accounts_for_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        # Validate sending account
        sending_account = self.get_account(sending_account_id)
        if not sending_account:
            raise ValidationError(f"Sending account with ID {sending_account_id} does not exist.")

        # Validate receiving account
        receiving_account = self.get_account(receiving_account_id)
        if not receiving_account:
            raise ValidationError(f"Receiving account with ID {receiving_account_id} does not exist.")

        # Validate the transaction amount
        amount = float(amount)
        if amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")

        overdraft_limit = 1000.00  # Overdraft limit in float

        # Calculate the current balance of the sending account
        current_balance = self.get_balance(sending_account_id)

        # Check if the transaction exceeds the overdraft limit
        if current_balance - amount + overdraft_limit < 0:
            raise ValidationError(f"Overdraft limit ({overdraft_limit}) overreached")

        return True

    def validate_account_for_atm(self, amount: float, account_id: UUID, pin: str) -> bool:
        account = self.get_account(account_id)
        if not account:
            raise ValidationError("Account not found.")

        if (account.type != "checking"):
            raise ValidationError(f"ATM transactions are allowed only for checking accounts.")

        if account.PIN != pin:
            raise ValidationError("Invalid PIN.")

        overdraft_limit = 1000.00  # Overdraft limit in float

        # Calculate the current balance of the sending account
        current_balance = self.get_balance(account_id)

        if current_balance - amount + overdraft_limit < 0:
            raise ValidationError(f"Overdraft limit ({overdraft_limit}) overreached")

        return True

    def deposit_savings(self, account_id: UUID, amount: float):
        if amount <= 0:
            raise ValidationError("Deposit amount must be greater than zero.")

        savings_account = self.get_account(account_id)
        if not savings_account:
            raise ValidationError(f"Account with ID {account_id} does not exist.")

        reference_account_id = savings_account.reference_account_id
        if not reference_account_id:
            raise ValidationError(f"Account with ID {reference_account_id} does not exist.")

        try:
            with transaction.atomic():
                self.validate_accounts_for_transaction(amount, reference_account_id, savings_account.account_id)
                self.transaction_service.create_new_transaction(
                    amount=amount,
                    sending_account_id=reference_account_id,
                    receiving_account_id=savings_account.account_id,
                )
        except Exception as e:
            raise ValidationError(f"Deposit failed: {str(e)}")

    def withdraw_savings(self, account_id: UUID, amount: float):
        amount = float(amount)
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be greater than zero.")

        savings_account = self.get_account(account_id)
        if not savings_account:
            raise ValidationError(f"Savings account with ID {account_id} does not exist.")

        reference_account_id = savings_account.reference_account_id
        if not reference_account_id:
            raise ValidationError(f"Account with ID {reference_account_id} does not exist.")

        try:
            with transaction.atomic():
                if amount > self.get_balance(savings_account.account_id):
                    raise ValidationError(f"Withdrawal amount ({amount}) exceeds balance.")
                self.transaction_service.create_new_transaction(
                    amount=amount,
                    sending_account_id=savings_account.account_id,
                    receiving_account_id=reference_account_id,
                )
        except Exception as e:
            raise ValidationError(f"Withdrawal failed: {str(e)}")