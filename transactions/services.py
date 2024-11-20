from datetime import datetime, timedelta
from uuid import UUID

from dependency_injector.wiring import Provide
from django.db import transaction
from marshmallow import ValidationError

from core.services import ITransactionService
from transactions.models import Transaction
from accounts.models import Account
from accounts.managers import AccountManager
from typing import Optional, List


class TransactionService(ITransactionService):
    def __init__(self, account_service: Provide("account_service")):
        self.account_service = account_service

    def create_transaction(self, sending_account: Account, receiving_account: Account, amount: float):
        pass

    def update_transaction(self, transaction_id: int, amount: float):
        pass

    def delete_transaction(self, transaction_id: int):
        pass


    def get_transaction_history(self, account_id: UUID, timeframe: str) -> List[dict]:
        """
        Fetch transactions based on account_id and timeframe.

        :param account_id: UUID of the account whose transactions are to be fetched.
        :param timeframe: Filter transactions by timeframe ('30_days', '60_days', or 'all_time').
        :return: A list of dictionaries containing transaction details.
        """

        # Determine the start date based on the timeframe
        if timeframe == "30_days":
            start_date = datetime.now() - timedelta(days=30)
        elif timeframe == "60_days":
            start_date = datetime.now() - timedelta(days=60)
        elif timeframe == "all_time":
            start_date = None
        else:
            raise ValueError("Invalid timeframe. Valid options are '30_days', '60_days', or 'all_time'.")

        # Query transactions sent or received by the account within the specified timeframe
        if start_date:
            sent_transactions = Transaction.objects.filter(
                sending_account_id=account_id, date__gte=start_date
            )
            received_transactions = Transaction.objects.filter(
                receiving_account_id=account_id, date__gte=start_date
            )
        else:
            sent_transactions = Transaction.objects.filter(sending_account_id=account_id)
            received_transactions = Transaction.objects.filter(receiving_account_id=account_id)

        # Combine sent and received transactions
        transactions = sent_transactions.union(received_transactions).order_by('-date')

        # Format the transaction history as a list of dictionaries
        transaction_history = [
            {
                "transaction_id": str(transaction.transaction_id),
                "sending_account_id": str(transaction.sending_account_id),
                "receiving_account_id": str(transaction.receiving_account_id),
                "amount": float(transaction.amount),
                "date": transaction.date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for transaction in transactions
        ]

        return transaction_history

    def create_new_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        # Wrap the operation in a transaction for safety
        try:
            with transaction.atomic():
                # Create the transaction record
                transaction_record = Transaction.objects.create(
                    sending_account_id=sending_account_id,
                    receiving_account_id=receiving_account_id,
                    amount=amount,
                    date=datetime.now()
                )
            return True
        except Exception as e:
            raise ValidationError(f"Transaction failed: {str(e)}")

class BankingServiceImplI(ITransactionService):
    def create_transaction(self, sending_account: Account, receiving_account: Account, amount: float) -> Transaction:
        # Ensure sufficient funds in the sending account
        if sending_account.balance < amount:
            raise ValueError("Insufficient funds in sending account.")

        # Create the transaction
        transaction = Transaction.objects.create(
            sending_account_id=sending_account,
            receiving_account_id=receiving_account,
            amount=amount
        )

        # Update balances after the transaction
        self.update_balance(sending_account, receiving_account, amount)
        return transaction

    def update_transaction(self, transaction_id: int, amount: float) -> Optional[Transaction]:
        transaction = Transaction.objects.filter(id=transaction_id).first()
        if transaction:
            transaction.amount = amount
            transaction.save()
        return transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        transaction = Transaction.objects.filter(id=transaction_id).first()
        if transaction:
            transaction.delete()
            return True
        return False

    def check_balance(self, account: Account) -> float:
        return account.balance

    def update_balance(self, sending_account: Account, receiving_account: Account, amount: float) -> None:
        sending_account.balance -= amount
        receiving_account.balance += amount
        sending_account.save()
        receiving_account.save()

class TradingServiceImplI(ITransactionService):
    def create_transaction(self):
        pass

    def update_transaction(self):
        pass

    def delete_transaction(self):
        pass

    def check_balance(self):
        pass

    def update_balance(self):
        pass