from django import forms
from transactions.models import Transaction

class TransactionForm(forms.ModelForm):
    receiving_account_id = forms.UUIDField()

    class Meta:
        model = Transaction
        fields = ['receiving_account_id', 'amount']


class SavingsTransactionForm(forms.Form):
    TRANSACTION_CHOICES = [
        ("deposit", "Deposit"),
        ("withdraw", "Withdraw"),
    ]

    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, widget=forms.Select)
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
