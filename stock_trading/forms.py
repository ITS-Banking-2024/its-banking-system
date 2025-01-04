from django import forms
from .models import Stock

class BuyStockForm(forms.Form):
    stock = forms.ModelChoiceField(queryset=Stock.objects.all())
    quantity = forms.IntegerField(min_value=1)
