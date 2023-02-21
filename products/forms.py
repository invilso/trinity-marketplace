from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'photo', 'price', 'nickname', 'server']
    
    widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'description': forms.Textarea(attrs={'class': 'form-control'}),
        'price': forms.NumberInput(attrs={'class': 'form-control'}),
        'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        'server': forms.Select(attrs={'class': 'form-control'})
    }