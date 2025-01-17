from django import forms

class BuyStockForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Quantity")


class SellStockForm(forms.Form):
    quantity = forms.IntegerField(min_value=1,label="Quantity")
