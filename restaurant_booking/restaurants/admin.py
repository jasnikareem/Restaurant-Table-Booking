from django.contrib import admin
from.models import Restaurant, Rating, Table, TimeSlot,TableAvailability,Booking

admin.site.register(Restaurant)
admin.site.register(Rating)
admin.site.register(Table)
admin.site.register(TimeSlot)
admin.site.register(TableAvailability)
admin.site.register(Booking)