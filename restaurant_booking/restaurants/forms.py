from django import forms
from .models import Restaurant, Table


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'seats'] # Remove 'restaurant' from here
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




class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        # Include all fields you want the user to be able to edit
        fields = ['name', 'location', 'food_type', 'offer', 'image']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'food_type': forms.TextInput(attrs={'class': 'form-control'}),
            'offer': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }        