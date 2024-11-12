from core.models import Stock as AbstractStock
from stock_trading.managers import StockManager
from django.db import models

class Stock(AbstractStock):

    objects : StockManager = StockManager()

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock"
