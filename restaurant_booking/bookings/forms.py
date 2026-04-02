from django import forms
from restaurants.models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # Temporarily use only ONE guaranteed field to stop the crash
        fields = ['restaurant']