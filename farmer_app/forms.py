# farmer_app/forms.py

from django import forms
from django.apps import apps

class FarmerProductForm(forms.ModelForm):
    class Meta:
        model = apps.get_model('product_app', 'Product')  # Use string reference to avoid direct import
        fields = ['name', 'description', 'price', 'quantity', 'image']
