from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from django.db import transaction
from marshmallow import ValidationError

from core.services import ITransactionService
from transactions.models import Transaction, StockTransaction


class TransactionService(ITransactionService):

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

    def create_new_stock_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID, stock_id: UUID, quantity: int, transaction_type: str) -> bool:
        # Wrap the operation in a transaction for safety
        try:
            with transaction.atomic():
                # Create the transaction record
                stock_transaction_record = StockTransaction.objects.create(
                    sending_account_id=sending_account_id,
                    receiving_account_id=receiving_account_id,
                    amount=amount,
                    date=datetime.now(),
                    stockId=stock_id,
                    quantity=quantity,
                    transaction_type=transaction_type
                )
            return True
        except Exception as e:
            raise ValidationError(f"Transaction failed: {str(e)}")


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
                "amount": str(transaction.amount),
                "date": transaction.date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for transaction in transactions
        ]

        return transaction_history

    def get_stock_transaction_history(self, account_id: UUID, timeframe: str) -> List[dict]:
        """
        Fetch stock-specific transaction history for a given account.

        :param account_id: UUID of the custody account.
        :param timeframe: Filter transactions by timeframe ('30_days', '60_days', or 'all_time').
        :return: A list of dictionaries containing stock transaction details.
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

        # Query stock transactions for the given account within the timeframe
        query = StockTransaction.objects.filter(
            receiving_account_id=account_id
        ) | StockTransaction.objects.filter(
            sending_account_id=account_id
        )

        if start_date:
            query = query.filter(date__gte=start_date)

        # Format the stock transaction history as a list of dictionaries
        stock_transaction_history = [
            {
                "transaction_id": str(transaction.transaction_id),
                "stock_id": str(transaction.stockId),
                "stock_symbol": None,
                "transaction_type": transaction.transaction_type,
                "quantity": transaction.quantity,
                "amount": str(transaction.amount),
                "date": transaction.date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for transaction in query
        ]

        return stock_transaction_history