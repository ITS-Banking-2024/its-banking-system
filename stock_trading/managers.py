from django.db import models
from django.db.models import QuerySet


class StockManager(models.Manager):
    def get_by_stock_name(self, stock_name: str):
        return self.filter(stock_name__iexact=stock_name)

    def get_by_stock_id(self, stock_id: str):
        return self.filter(stockID=stock_id)

    def get_all_stocks(self) -> QuerySet:
        return self.all()