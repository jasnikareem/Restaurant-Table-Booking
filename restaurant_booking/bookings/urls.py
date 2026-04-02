from django.urls import path
from . import views

urlpatterns = [
    
    path('my-bookings/', views.manage_bookings, name='manage_bookings'),
    
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    path('add-booking/', views.add_booking, name='add_booking'),
    
    path('book-table/<int:restaurant_id>/', views.book_table, name='book_table'),
    
    path('select-menu/<int:booking_id>/', views.select_menu, name='select_menu'),
    
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
]
 

