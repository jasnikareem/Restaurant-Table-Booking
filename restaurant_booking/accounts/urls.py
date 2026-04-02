# accounts/urls.py
from django.urls import path
from . import views  
from restaurants import views as restaurant_views 

urlpatterns = [
    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
    
    path('register/', views.register, name='register'),
    
    path('admin_dashboard/' ,views.admin_dashboard, name='admin_dashboard'),
    
    path('restaurant_dashboard/', restaurant_views.restaurant_owner_dashboard, name='restaurant_owner_dashboard'),
    
    path('home/', views.home, name='home'),
    
    path('manage-restaurants/', views.manage_restaurants, name='manage_restaurants'),
    
    path('bookings/', views.view_bookings, name='view_bookings'),
    
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
   
   path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
   
   path('manage_users/', views.manage_users, name='manage_users'),
   
   path('offers/', views.offers, name='offers'),
   
   path('offers/delete/<int:restaurant_id>/', views.delete_offer, name='delete_offer'),
   
   path('offers/add/<int:restaurant_id>/', views.add_offer, name='add_offer'),
   
   path('offers/edit/<int:restaurant_id>/', views.edit_offer, name='edit_offer'),
   
   path('manage-timeslots/<int:restaurant_id>/', views.manage_timeslots, name='manage_timeslots'),
   
   path('delete-slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),


]