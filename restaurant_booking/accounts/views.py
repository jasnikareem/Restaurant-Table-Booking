from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from restaurants.models import Restaurant, Booking, Table, TimeSlot

# --- HELPER FUNCTIONS ---

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# --- AUTHENTICATION VIEWS ---

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Role-based redirect
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'owner':
                return redirect('restaurant_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        location = request.POST.get('location')
        role = request.POST.get('role', 'customer').lower()
        
        if role == 'admin': 
            messages.error(request, 'Manual registration for Admin role is not allowed.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')

        User.objects.create_user(
            username=username,
            password=password,
            role=role,
            location=location
        )
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
        
    return render(request, 'accounts/register.html')


# --- DASHBOARDS ---

@login_required
def home(request):
    # Main landing page for customers, redirects staff to dashboards.
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'owner':
        return redirect('restaurant_dashboard')

    # Filter restaurants by user location 
    restaurants = Restaurant.objects.filter(location__iexact=request.user.location)
    return render(request, 'accounts/homepage.html', {'restaurants': restaurants})


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.warning(request, "Access denied.")
        return redirect('home')

    # Add 'total_tables' to your context here
    context = {
        'total_users': User.objects.count(),
        'total_restaurants': Restaurant.objects.count(),
        'total_bookings': Booking.objects.count(),
        'total_tables': Table.objects.count(),  
    }
    return render(request, 'accounts/admin_dashboard.html', context)


# --- ADMIN MANAGEMENT VIEWS ---

@login_required
def manage_users(request):
    if request.user.role != 'admin':
        return redirect('home')
    users = User.objects.all()
    return render(request, 'accounts/manage_users.html', {'users': users})


@login_required
def edit_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('home')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        user.location = request.POST.get('location', user.location)
        user.save()
        messages.success(request, f'User {user.username} updated.')
        return redirect('manage_users')

    return render(request, 'accounts/edit_user.html', {'user': user})


@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot delete your own admin account.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('manage_users')



@login_required
def manage_restaurants(request):
    if request.user.role not in ['admin', 'owner']:
        messages.error(request, "Access denied.")
        return redirect('home')

    # If admin, show everything. If owner, only show THEIR restaurants.
    if request.user.role == 'admin':
        restaurants = Restaurant.objects.all().select_related('owner')
    else:
        restaurants = Restaurant.objects.filter(owner=request.user)
    
    return render(request, 'accounts/manage_restaurants.html', {
        'restaurants': restaurants
    })


# --- BOOKINGS & OFFERS ---

@login_required
def view_bookings(request):
    if request.user.role == 'admin':
        bookings = Booking.objects.all()
    elif request.user.role == 'owner':
        bookings = Booking.objects.filter(restaurant__owner=request.user)
    else:
        bookings = Booking.objects.filter(user=request.user)

    return render(request, 'accounts/view_bookings.html', {'bookings': bookings})


@login_required
def offers(request):
    if request.user.role == 'admin':
        # Admin sees every restaurant with an offer
        restaurants = Restaurant.objects.filter(offer__gt=0)
    elif request.user.role == 'owner':
        # Owners only see their own active offers here to manage them
        restaurants = Restaurant.objects.filter(owner=request.user, offer__gt=0)
    else:
        # Customers see offers in their specific location
        restaurants = Restaurant.objects.filter(
            location__iexact=request.user.location, 
            offer__gt=0
        )
        
    return render(request, 'accounts/offers.html', {'restaurants': restaurants})


@login_required
def add_offer(request, restaurant_id): 
    #Allows Admin or Owners to set an offer on a specific restaurant.
    
    # 1. Get the specific restaurant first
    target_res = get_object_or_404(Restaurant, id=restaurant_id)

    # 2. Security Check
    if request.user.role == 'admin' or target_res.owner == request.user:
        if request.method == 'POST':
            offer_val = request.POST.get('offer')
            
            if offer_val:
                target_res.offer = int(offer_val)
                target_res.save()
                messages.success(request, f"Offer added to {target_res.name}!")
                return redirect('manage_restaurants') # Redirect back to dashboard
            else:
                messages.error(request, "Please enter a valid offer percentage.")
    else:
        messages.error(request, "Access denied. You don't own this restaurant.")
        return redirect('manage_restaurants')

    return render(request, 'accounts/add_offer.html', {'restaurant': target_res})


@login_required
def edit_offer(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Permission Check: Only admin or the specific restaurant owner
    if request.user.role != 'admin' and restaurant.owner != request.user:
        messages.error(request, "You do not have permission to edit this offer.")
        return redirect('offers')

    if request.method == 'POST':
        new_offer = request.POST.get('offer')
        try:
            restaurant.offer = int(new_offer)
            restaurant.save()
            messages.success(request, f"Offer for {restaurant.name} updated.")
            return redirect('offers')
        except (ValueError, TypeError):
            messages.error(request, "Invalid number.")

    return render(request, 'accounts/edit_offer.html', {'restaurant': restaurant})


@login_required
def delete_offer(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.user.role == 'admin' or restaurant.owner == request.user:
        restaurant.offer = 0
        restaurant.save()
        messages.success(request, "Offer removed.")
    else:
        messages.error(request, "Permission denied.")
        
    return redirect('offers')


def manage_timeslots(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    slots = TimeSlot.objects.filter(restaurant=restaurant).order_by('start_time')

    if request.method == "POST":
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        
        if start and end:
            TimeSlot.objects.create(
                restaurant=restaurant, 
                start_time=start, 
                end_time=end
            )
            return redirect('manage_timeslots', restaurant_id=restaurant.id)

    return render(request, 'accounts/manage_timeslots.html', {
        'restaurant': restaurant,
        'slots': slots
    })



def delete_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    restaurant_id = slot.restaurant.id # Save the ID before deleting
    
    if request.method == "POST":
        slot.delete()
        
    return redirect('manage_timeslots', restaurant_id=restaurant_id)