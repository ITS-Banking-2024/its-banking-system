from django import forms
from stock_trading.models import Stock

class BuyStockForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Quantity")
