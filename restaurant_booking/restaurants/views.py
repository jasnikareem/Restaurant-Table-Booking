import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count, Avg
from .forms import TableForm, RestaurantForm
from django.db.models import Count
from .models import Restaurant, Rating, TimeSlot, Table,Booking
from django.utils import timezone

User = get_user_model()

# --- HELPER FUNCTIONS ---
def _has_management_rights(user, restaurant):
    """Check if a user is the owner of the restaurant or a platform admin."""
    return restaurant.owner == user or getattr(user, 'role', None) == 'admin'

# --- RESTAURANT VIEWS ---

def restaurant_list(request):
    """Public list of restaurants with location search."""
    location = request.GET.get('location', '').strip()
    restaurants = Restaurant.objects.all()

    if location:
        restaurants = restaurants.filter(location__icontains=location)

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants,
        'search_location': location
    })

def restaurant_detail(request, restaurant_id):
    """Detailed view for a single restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    ratings = Rating.objects.filter(restaurant=restaurant)
    slots = TimeSlot.objects.filter(restaurant=restaurant)
    tables = Table.objects.filter(restaurant=restaurant)

    is_owner = False
    if request.user.is_authenticated:
        is_owner = _has_management_rights(request.user, restaurant)

    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    return render(request, 'restaurants/details.html', {
        'restaurant': restaurant,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'is_owner': is_owner,
        'slots': slots,
        'tables': tables
    })

@login_required
def add_restaurant(request):
    """Admin or Owner registration of a new restaurant."""
    if getattr(request.user, 'role', None) not in ['admin', 'owner']:
        messages.error(request, "Access Denied: Only Admins or Owners can register restaurants.")
        return redirect('home')

    # Logic for the owner dropdown
    if request.user.role == 'admin':
        all_owners = User.objects.filter(role='owner')
    else:
        all_owners = User.objects.filter(id=request.user.id)

    if request.method == "POST":
        name = request.POST.get('name')
        location = request.POST.get('location')
        owner_id = request.POST.get('owner')
        
        if name and location and owner_id:
            try:
                owner = User.objects.get(id=owner_id)
                Restaurant.objects.create(
                    name=name,
                    location=location,
                    food_type=request.POST.get('food_type'),
                    offer=request.POST.get('offer'),
                    image=request.FILES.get('image'),
                    owner=owner
                )
                messages.success(request, f"{name} registered successfully!")
                return redirect('manage_restaurants')
            except User.DoesNotExist:
                messages.error(request, "Selected owner does not exist.")
        else:
            messages.error(request, "Required fields are missing.")

    return render(request, 'restaurants/add_restaurant.html', {'all_owners': all_owners})

@login_required
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if not _has_management_rights(request.user, restaurant):
        messages.error(request, "You do not have permission to delete this.")
        return redirect('home')

    if request.method == "POST":
        restaurant.delete()
        messages.success(request, "Restaurant deleted successfully.")
        return redirect('manage_restaurants') 
        
    return render(request, 'restaurants/delete_restaurant.html', {'restaurant': restaurant})

# --- DATA MANAGEMENT (Slots & Tables) ---

@login_required
def add_table(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.restaurant = restaurant  # Link it to the current restaurant
            table.save()
            messages.success(request, f"Table {table.table_number} added!")
            return redirect('manage_tables', restaurant_id=restaurant.id)
    else:
        form = TableForm()
    
    return render(request, 'restaurants/add_table.html', {'form': form, 'restaurant': restaurant})

@login_required
def add_timeslot(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if not _has_management_rights(request.user, restaurant):
        return redirect('restaurant_detail', restaurant_id=restaurant.id)

    if request.method == "POST":
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        if start and end:
            TimeSlot.objects.create(restaurant=restaurant, start_time=start, end_time=end)
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
            
    return render(request, 'restaurants/add_timeslot.html', {'restaurant': restaurant})

# --- REVIEWS & RATINGS ---
@login_required
def add_review(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if the user is the owner (Owners shouldn't review their own place)
    if restaurant.owner == request.user:
        messages.error(request, "You cannot review your own restaurant.")
        return redirect('restaurant_detail', restaurant_id=restaurant.id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Rating.objects.create(
                restaurant=restaurant,
                user=request.user,
                rating=rating,
                review=comment # Your model uses 'review', form uses 'comment'
            )
            messages.success(request, "Review added!")
        else:
            messages.error(request, "Please provide both a rating and a comment.")
            
    return redirect('restaurant_detail', restaurant_id=restaurant.id)

# --- DASHBOARDS ---
@login_required
def restaurant_owner_dashboard(request):
    # 1. Safety Check: Only allow 'owner' role to see this
    if getattr(request.user, 'role', None) != 'owner':
        messages.error(request, "Access Denied: This dashboard is for Restaurant Owners.")
        return redirect('home')

    # 2. Filter Restaurants: ONLY those owned by the current user
    my_restaurants = Restaurant.objects.filter(owner=request.user)
    
    # 3. Filter Bookings: ONLY bookings for the owner's restaurants
    all_bookings = Booking.objects.filter(restaurant__in=my_restaurants)
    
    # Analytics Calculations
    total_bookings = all_bookings.count()
    today = timezone.now().date()
    today_bookings = all_bookings.filter(date=today).count() # Changed from created_at to date for accuracy

    # Chart Data (Last 7 Days)
    line_data_qs = (
        all_bookings.filter(date__gte=today - timezone.timedelta(days=7))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    line_labels = json.dumps([str(item['date']) for item in line_data_qs])
    line_counts = json.dumps([item['count'] for item in line_data_qs])

    context = {
        'my_restaurants': my_restaurants,
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'line_labels': line_labels,
        'line_counts': line_counts,
        'restaurant_count': my_restaurants.count(),
    }

    return render(request, 'restaurants/restaurant_dashboard.html', context)


def manage_tables(request, restaurant_id):
    # 1. Fetch the restaurant first
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # 2. SECURITY CHECK: Only Admin or Owner can pass
    if not request.user.is_staff and restaurant.owner != request.user:
        messages.error(request, "You do not have permission to manage these tables.")
        # Dynamic redirect: Admins go to Admin Dash, Owners go to Restaurant Dash
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('restaurant_dashboard')

    # 3. Handle POST Actions (Add or Delete)
    if request.method == "POST":
        
        # --- LOGIC: DELETE TABLE ---
        if 'delete_table_id' in request.POST:
            table_id = request.POST.get('delete_table_id')
            table_to_delete = get_object_or_404(Table, id=table_id, restaurant=restaurant)
            table_number = table_to_delete.table_number
            table_to_delete.delete()
            
            messages.success(request, f"Table {table_number} has been removed.")
            return redirect('manage_tables', restaurant_id=restaurant.id)

        # --- LOGIC: ADD NEW TABLE ---
        table_number = request.POST.get('table_number')
        capacity = request.POST.get('capacity')
        
        if table_number and capacity:
            Table.objects.create(
                restaurant=restaurant,
                table_number=table_number,
                seats=capacity
            )
            messages.success(request, f"Table {table_number} added successfully!")
            return redirect('manage_tables', restaurant_id=restaurant.id)

    # 4. DATA RETRIEVAL (For the table list)
    tables = restaurant.table_set.all().order_by('table_number')
    
    # 5. RENDER THE PAGE
    return render(request, 'restaurants/manage_tables.html', {
        'restaurant': restaurant,
        'tables': tables,
        'is_admin': request.user.is_staff
    })

def edit_table(request, restaurant_id, table_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if user is either the owner OR an admin
    if not request.user.is_staff and restaurant.owner != request.user:
        messages.error(request, "Access denied.")
        return redirect('restaurant_dashboard')

    table = get_object_or_404(Table, id=table_id, restaurant=restaurant)

    if request.method == 'POST':
        table.table_number = request.POST.get('table_number')
        table.seats = request.POST.get('capacity')
        table.save()
        messages.success(request, f"Table {table.table_number} updated successfully.")
        return redirect('manage_tables', restaurant_id=restaurant.id)

    return render(request, 'restaurants/edit_table.html', {
        'restaurant': restaurant,
        'table': table,
        'is_admin': request.user.is_staff
    })

@login_required
def edit_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if not _has_management_rights(request.user, restaurant):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    if request.method == 'POST':
        # Manually grab data from the request.POST dictionary
        restaurant.name = request.POST.get('name')
        restaurant.location = request.POST.get('location')
        restaurant.food_type = request.POST.get('food_type')
        restaurant.offer = request.POST.get('offer')
        
        # Handle the image only if a new one is uploaded
        if request.FILES.get('image'):
            restaurant.image = request.FILES.get('image')
            
        restaurant.save()
        messages.success(request, f"{restaurant.name} updated successfully!")
        
        if request.user.role == 'admin':
            return redirect('manage_restaurants')
        return redirect('restaurant_dashboard')

    return render(request, 'restaurants/edit_restaurant.html', {
        'restaurant': restaurant
    })