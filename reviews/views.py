from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from rentals.models import Rental

@login_required
def add_review(request, rental_pk):
    rental = get_object_or_404(Rental, pk=rental_pk, renter=request.user, status='returned')

    if hasattr(rental, 'review'):
        messages.info(request, 'You already reviewed this rental.')
        return redirect('dashboard')

    if request.method == 'POST':
        Review.objects.create(
            rental=rental,
            reviewer=request.user,
            tool=rental.tool,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment', ''),
        )
        messages.success(request, 'Review submitted!')
        return redirect('dashboard')

    return render(request, 'add_review.html', {'rental': rental})