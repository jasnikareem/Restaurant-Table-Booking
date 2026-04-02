from django.db import models

# Create your models here.
from restaurants.models import Restaurant

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu')
    category = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    

    