from django.contrib import admin

from stock_trading.models import Stock, StockOwnership

admin.site.register(Stock)
admin.site.register(StockOwnership)