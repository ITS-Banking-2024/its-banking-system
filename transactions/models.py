import uuid

from django.db import models
from core.models import Transaction
from transactions.settings import ACCOUNT_MODEL


class TransactionBase(Transaction):
    sending_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='base_sent_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    receiving_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='base_received_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class Transaction(TransactionBase):
    sending_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='sent_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    receiving_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='received_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "transaction"


class StockTransaction(TransactionBase):
    sending_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='stock_sent_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    receiving_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='stock_received_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    stockId = models.ForeignKey('stock_trading.Stock', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=4, choices=[('buy', 'Buy'), ('sell', 'Sell')])

    class Meta:
        db_table = "transaction_stock"


class ATMTransaction(TransactionBase):
    sending_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='atm_sent_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    receiving_account_id = models.ForeignKey(
        ACCOUNT_MODEL,
        related_name='atm_received_transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    atmId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        db_table = "transaction_atm"
