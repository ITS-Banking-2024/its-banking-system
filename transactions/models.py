import uuid
from django.db import models
from core.models import Transaction


class TransactionBase(Transaction):
    sending_account_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the sending account"
    )
    receiving_account_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the receiving account"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"Transaction {self.transaction_id} of amount {self.amount}"



class Transaction(TransactionBase):
    class Meta:
        db_table = "transaction"


class StockTransaction(TransactionBase):
    stockId = models.ForeignKey('stock_trading.Stock', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(
        max_length=4,
        choices=[('buy', 'Buy'), ('sell', 'Sell')]
    )

    class Meta:
        db_table = "transaction_stock"


class ATMTransaction(TransactionBase):
    atmId = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    class Meta:
        db_table = "transaction_atm"
