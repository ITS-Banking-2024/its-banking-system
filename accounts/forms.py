from django import forms
from transactions.models import Transaction

class TransactionForm(forms.ModelForm):
    receiving_account_id = forms.UUIDField()

    class Meta:
        model = Transaction
        fields = ['receiving_account_id', 'amount']