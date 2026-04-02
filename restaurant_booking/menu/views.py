
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Menu
from restaurants.models import Restaurant
from django.contrib import messages



# Helper function to check permissions (DRY - Don't Repeat Yourself)
def has_permission(user, restaurant):
    return user.role == 'admin' or restaurant.owner == user

def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menus = Menu.objects.filter(restaurant=restaurant)
    categories = menus.values_list('category', flat=True).distinct()

    # Bulletproof check for Admin or Owner
    is_owner = False
    if request.user.is_authenticated:
        user_role = str(request.user.role).lower() # Handles 'Admin' or 'admin'
        if user_role == 'admin' or restaurant.owner == request.user:
            is_owner = True

    return render(request, 'menu/restaurant_menu.html', {
        'restaurant': restaurant,
        'menus': menus,
        'categories': categories,
        'is_owner': is_owner,
    })


@login_required
def add_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if not has_permission(request.user, restaurant):
        messages.error(request, "Access Denied: You don't own this restaurant.")
        return redirect('home')

    if request.method == "POST":
        Menu.objects.create(
            restaurant=restaurant,
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            category=request.POST.get('category'),
            image=request.FILES.get('image')
        )
        messages.success(request, f"'{request.POST.get('name')}' added successfully!")
        return redirect('restaurant_menu', restaurant_id=restaurant.id)

    return render(request, 'menu/add_menu.html', {'restaurant': restaurant})

@login_required
def edit_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    
    # Security check added
    if not has_permission(request.user, menu.restaurant):
        return redirect('home')

    if request.method == "POST":
        menu.name = request.POST.get('name')
        menu.price = request.POST.get('price')
        menu.category = request.POST.get('category')
        if request.FILES.get('image'):
            menu.image = request.FILES.get('image')
        menu.save()
        return redirect('restaurant_menu', restaurant_id=menu.restaurant.id)

    return render(request, 'menu/edit_menu.html', {'menu': menu})

@login_required
def delete_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    
    # Security check added
    if not has_permission(request.user, menu.restaurant):
        return redirect('home')

    restaurant_id = menu.restaurant.id
    menu.delete()
    return redirect('restaurant_menu', restaurant_id=restaurant_id)