from django.contrib import admin

from transactions.models import Transaction, StockTransaction, ATMTransaction

admin.site.register(Transaction)
admin.site.register(StockTransaction)
admin.site.register(ATMTransaction)