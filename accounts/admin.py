from django.contrib import admin

from accounts.models import CheckingAccount, SavingsAccount, CustodyAccount

admin.site.register(CheckingAccount)
admin.site.register(SavingsAccount)
admin.site.register(CustodyAccount)