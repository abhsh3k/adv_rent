from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime

from .models import Rental, Message
from tools.models import Tool
from toolx.notifications import (
    notify_new_rental_request,
    notify_rental_approved,
    notify_rental_declined,
    notify_tool_returned,
    notify_new_message,
)

@login_required
def rent_tool(request, pk):
    tool = get_object_or_404(Tool, pk=pk)

    # 1. Verification Check
    if not request.user.is_verified:
        messages.warning(request, 'You need to verify your ID before renting.')
        return redirect('verify_id')

    if request.method == 'POST':
        start = request.POST.get('start_date')
        end   = request.POST.get('end_date')

        if not start or not end:
            messages.error(request, 'Please select both start and end dates.')
            return redirect('tool_detail', pk=pk)

        # 2. Safe Date Parsing
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date   = datetime.strptime(end, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('tool_detail', pk=pk)

        if end_date <= start_date:
            messages.error(request, 'End date must be after start date.')
            return redirect('tool_detail', pk=pk)

        # 3. FIX: Assign the created object to the variable 'rental'
        rental = Rental.objects.create(
            tool=tool,
            renter=request.user,
            start_date=start_date,
            end_date=end_date,
            message=request.POST.get('message', ''),
        )
        
        # Now 'rental' is defined and can be passed to the notification
        notify_new_rental_request(rental)
        
        messages.success(request, f'Rental request sent to {tool.owner.first_name or tool.owner.username}!')
        return redirect('dashboard')

    return redirect('tool_detail', pk=pk)


@login_required
def rental_action(request, pk, action):
    rental = get_object_or_404(Rental, pk=pk)
    owner = rental.tool.owner

    # Approve Logic
    if action == 'approve' and request.user.pk == owner.pk:
        rental.status = 'active'
        rental.tool.is_available = False
        rental.tool.save()
        rental.save()
        notify_rental_approved(rental)
        messages.success(request, 'Rental approved!')

    # Decline Logic
    elif action == 'decline' and request.user.pk == owner.pk:
        rental.status = 'cancelled'
        rental.save()
        notify_rental_declined(rental)
        messages.info(request, 'Rental declined.')

    # Return Logic
    elif action == 'return' and request.user.pk == owner.pk:
        rental.status = 'returned'
        rental.tool.is_available = True
        rental.tool.save()
        rental.save()
        notify_tool_returned(rental)
        messages.success(request, 'Tool marked as returned!')

    # Cancel Logic (by Renter)
    elif action == 'cancel' and request.user.pk == rental.renter.pk:
        rental.status = 'cancelled'
        rental.save()
        messages.info(request, 'Rental cancelled.')

    else:
        messages.error(request, 'Action not allowed.')

    return redirect('dashboard')


@login_required
def rental_thread(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    
    is_renter = request.user.pk == rental.renter.pk
    is_owner  = request.user.pk == rental.tool.owner.pk

    if not is_renter and not is_owner:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    # Mark incoming messages as read
    rental.messages.exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                rental=rental,
                sender=request.user,
                body=body,
            )
            # Determine who gets the notification
            recipient = rental.tool.owner if is_renter else rental.renter
            notify_new_message(rental, request.user, recipient, body[:100])
            
        return redirect('rental_thread', pk=pk)

    thread = rental.messages.select_related('sender').all()
    return render(request, 'rental_thread.html', {
        'rental': rental,
        'thread': thread,
    })


@login_required
def inbox(request):
    # Fetch rentals where the user is involved
    rentals = Rental.objects.filter(
        Q(renter=request.user) | Q(tool__owner=request.user)
    ).select_related('tool', 'renter', 'tool__owner').order_by('-updated_at')

    inbox_items = []
    for rental in rentals:
        last_msg = rental.messages.last()
        unread = rental.messages.exclude(sender=request.user).filter(is_read=False).count()
        
        # Identify the "other person" in the conversation
        if request.user.pk == rental.renter.pk:
            other_person = rental.tool.owner
        else:
            other_person = rental.renter

        inbox_items.append({
            'rental': rental,
            'last_msg': last_msg,
            'unread': unread,
            'other_person': other_person,
        })

    return render(request, 'inbox.html', {'inbox_items': inbox_items})