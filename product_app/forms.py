# product_app/forms.py

from django import forms
from .models import Product
import os

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'quantity', 'description', 'image', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Product Name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input price-input',
                'min': '10',
                'step': '1',
                'placeholder': '0.00'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'placeholder': 'Available Quantity'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Product Description'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero")
        return price

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check if it's a new file upload
            if hasattr(image, 'size'):
                if image.size > 5 * 1024 * 1024:  # 5MB limit
                    raise forms.ValidationError("Image file too large ( > 5MB )")
                
                # Validate image format
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in valid_extensions:
                    raise forms.ValidationError("Unsupported file format. Please use JPG, PNG or GIF")
        return image
