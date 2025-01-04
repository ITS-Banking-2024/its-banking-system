from django.contrib import admin
from .models import CheckingAccount, SavingsAccount, CustodyAccount


@admin.register(CheckingAccount)
class CheckingAccountAdmin(admin.ModelAdmin):
    exclude = ('type',)


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    exclude = ('type', 'opening_balance')


@admin.register(CustodyAccount)
class CustodyAccountAdmin(admin.ModelAdmin):
    exclude = ('type',)
