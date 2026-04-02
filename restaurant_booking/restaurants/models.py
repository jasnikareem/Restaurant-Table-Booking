from django.db import models
from accounts.models import User
from django.conf import settings

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    food_type = models.CharField(max_length=50)
    image = models.ImageField(upload_to='restaurants')
    offer = models.IntegerField(default=0)
    location = models.CharField(max_length=100) 
    
    
    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    table_number = models.IntegerField()
    seats = models.IntegerField()

    def __str__(self):
        return f"Table {self.table_number}"
        

class TimeSlot(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"



class TableAvailability(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.table.restaurant.name} - Table {self.table.table_number} at {self.timeslot}"
    


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    guests = models.PositiveIntegerField(default=1)
    menus = models.ManyToManyField('menu.Menu', blank=True)

    def __str__(self):
        return f"Booking for {self.user.username} at {self.restaurant.name} on {self.date}"





class Rating(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    