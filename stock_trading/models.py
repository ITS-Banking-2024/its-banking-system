from core.models import Stock as AbstractStock
from stock_trading.managers import StockManager
from django.db import models

from stock_trading.settings import ACCOUNT_MODEL


class Stock(AbstractStock):

    objects : StockManager = StockManager()

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock"

class StockOwnership(models.Model):
    account = models.ForeignKey(ACCOUNT_MODEL, on_delete=models.PROTECT, related_name="account")
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name="stock")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "stock_ownership"
        unique_together = ('account', 'stock')