from core.services import ITransactionService
from transactions.models import Transaction
from accounts.models import Account
from typing import Optional

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