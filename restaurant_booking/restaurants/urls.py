from django.urls import path
from . import views

urlpatterns = [
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    
    # Dashboard (The main page for Owners)
    path('dashboard/', views.restaurant_owner_dashboard, name='restaurant_dashboard'),

    path('add_restaurant/', views.add_restaurant, name='add_restaurant'),
    
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    
    path('restaurant/delete/<int:restaurant_id>/', views.delete_restaurant, name='delete_restaurant'),
    
    path('edit-restaurant/<int:restaurant_id>/', views.edit_restaurant, name='edit_restaurant'),

    path('add-table/<int:restaurant_id>/', views.add_table, name='add_table'),
    
    path('add_timeslot/<int:restaurant_id>/', views.add_timeslot, name='add_timeslot'),
    
    path('rating/<int:restaurant_id>/', views.add_review, name='add_rating'),
    
    path('restaurant/<int:restaurant_id>/add_review/', views.add_review, name='add_review'),
    
    path('manage-tables/<int:restaurant_id>/', views.manage_tables, name='manage_tables'),
    
    path('restaurants/<int:restaurant_id>/table/edit/<int:table_id>/', views.edit_table, name='edit_table'),
]