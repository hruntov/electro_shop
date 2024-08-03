from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    """Form for adding products to the shopping cart or updating quantities."""
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int, label='Кількість')
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
