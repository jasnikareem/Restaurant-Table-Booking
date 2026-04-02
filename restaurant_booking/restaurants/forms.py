from django import forms
from .models import Restaurant, Table


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'seats'] 
        widgets = {
            'table_number': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. 101'
            }),
            'seats': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. 4'
            }),
        }



