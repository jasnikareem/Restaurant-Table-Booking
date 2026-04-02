from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from restaurants.models import Restaurant, Table, TimeSlot,Booking
from menu.models import Menu
from django.contrib import messages


# Book table


@login_required
def book_table(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    slots = TimeSlot.objects.filter(restaurant=restaurant)
    
    selected_date = request.GET.get('date')
    selected_slot = request.GET.get('slot')
    
    # Logic for GET: Filter out tables already booked for the chosen date/slot
    available_tables = Table.objects.filter(restaurant=restaurant)
    if selected_date and selected_slot:
        booked_table_ids = Booking.objects.filter(
            date=selected_date,
            timeslot_id=selected_slot
        ).exclude(status='cancelled').values_list('table_id', flat=True)
        available_tables = available_tables.exclude(id__in=booked_table_ids)

    if request.method == 'POST':
        date = request.POST.get('date')
        slot_id = request.POST.get('slot')
        table_id = request.POST.get('table')
        guests = request.POST.get('guests')

        # --- NEW: DOUBLE CHECK AVAILABILITY ON SUBMIT ---
        is_taken = Booking.objects.filter(
            date=date, 
            timeslot_id=slot_id, 
            table_id=table_id
        ).exclude(status='cancelled').exists()

        if is_taken:
            messages.error(request, "Sorry, this table was just booked by someone else! Please choose another.")
            # Stay on the page so they can pick a different table
        else:
            new_booking = Booking.objects.create(
                user=request.user,
                restaurant=restaurant,
                date=date,
                timeslot_id=slot_id,
                table_id=table_id,
                guests=guests,
                status='confirmed'
            )
            return redirect('select_menu', booking_id=new_booking.id)

    return render(request, "booking/book_table.html", {
        "restaurant": restaurant,
        "tables": available_tables,
        "slots": slots,
        "selected_date": selected_date,
        "selected_slot": selected_slot
    })
  
@login_required
def booking_success(request, booking_id):
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    
    return render(request, 'booking/booking_success.html', {
        'booking': booking,
        'restaurant': booking.restaurant
    })


# Manage bookings

@login_required
def manage_bookings(request):
    # Admin sees everything
    if request.user.role == 'admin':
        bookings = Booking.objects.all() 

    # Owner (Restaurant Owner) sees bookings for their specific restaurants
    elif request.user.role == 'owner':
        bookings = Booking.objects.filter(restaurant__owner=request.user)

    # Customers see only their own bookings
    else:
        bookings = Booking.objects.filter(user=request.user)

    return render(request, "booking/manage_bookings.html", {"bookings": bookings})

# Cancel booking

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user != request.user and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        # FIX: Change 'my_bookings' to 'manage_bookings'
        return redirect('manage_bookings') 

    booking.delete() 
    messages.success(request, "Booking cancelled successfully.")
    
    # FIX: Change 'my_bookings' to 'manage_bookings'
    return redirect('manage_bookings')



# Edit booking
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    restaurant = booking.restaurant
    
    if request.method == 'POST':
        # 1. Get the data from the form names in your HTML
        new_date = request.POST.get('date')
        new_slot_id = request.POST.get('timeslot') # Matches name="timeslot" in HTML
        new_table_id = request.POST.get('table')   # Matches name="table" in HTML
        new_guests = request.POST.get('guests')    # Matches name="guests" in HTML

        # 2. Update the booking object attributes
        booking.date = new_date
        booking.timeslot_id = new_slot_id
        booking.table_id = new_table_id
        booking.guests = new_guests
        
        # 3. Save to database
        booking.save()
        
        messages.success(request, "Booking updated successfully!")
        
        # 4. Use 'manage_bookings' because that is the name of your list view
        return redirect('manage_bookings') 

    # --- GET Logic ---
    slots = TimeSlot.objects.filter(restaurant=restaurant)
    tables = Table.objects.filter(restaurant=restaurant)
    
    return render(request, 'booking/edit_booking.html', {
        'booking': booking,
        'slots': slots,
        'tables': tables,
        'restaurant': restaurant,
    })
# Add booking using form

@login_required
def add_booking(request):

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            return redirect("booking/booking_success.html")

    else:
        form = BookingForm()

    return render(request, "booking/booking_form.html", {
        "form": form
    })


@login_required
def select_menu(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    restaurant = booking.restaurant
    
    
    menus = Menu.objects.filter(restaurant=restaurant)

    if request.method == "POST":
        selected_menu_ids = request.POST.getlist("menu")
        booking.menus.set(selected_menu_ids)
        
        return redirect("booking_success", booking_id=booking.id)

    
    return render(request, "booking/select_menu.html", {
        "booking": booking,
        "menus": menus
    })