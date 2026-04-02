from django.urls import path
from . import views

urlpatterns = [
    
    path('restaurant/<int:restaurant_id>/', views.restaurant_menu, name='restaurant_menu'),
    
    path('add/<int:restaurant_id>/', views.add_menu, name='add_menu'),
    
    path('edit/<int:menu_id>/', views.edit_menu, name='edit_menu'),
    
    path('delete/<int:menu_id>/', views.delete_menu, name='delete_menu'),

]