from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import math
from datetime import date
from .models import Tool, Category  # Ensure Category is imported
from django.contrib.auth import get_user_model

User = get_user_model()


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def home(request):
    # 1. Fetch 3-5 random tools for the Hero section
    # .order_by('?') is the Django way to randomize on every reload
    hero_tools = Tool.objects.filter(is_available=True).exclude(image="").order_by('?')[:3]
    
    # 2. Fetch the latest 8 tools for the "Just Listed" section
    latest_tools = Tool.objects.filter(is_available=True).order_by('-created_at')[:8]

    return render(request, 'home.html', {
        'hero_tools': hero_tools,
        'latest_tools': latest_tools,
        'categories': Category.objects.all(),
        'total_tools': Tool.objects.count(),
        'total_users': User.objects.count(),
        # Optional: Add a placeholder for total rentals if you have a Rental model
        'total_rentals': 800 # Or Rental.objects.count()
    })

def tool_list(request):
    tools = Tool.objects.all()
    # Fetch all categories from the DB
    all_categories = Category.objects.all()

    # Search
    q = request.GET.get('q')
    if q:
        tools = tools.filter(name__icontains=q)

    # Filter by category - Use category slug or ID depending on your frontend
    category_slug = request.GET.get('category')
    if category_slug:
        tools = tools.filter(category__slug=category_slug) # Adjusted for Model relation

    # Filter by availability
    if request.GET.get('available') == 'yes':
        tools = tools.filter(is_available=True)

    # Sort
    sort = request.GET.get('sort', 'newest')
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    if sort == 'nearest' and user_lat and user_lng:
        tools_list = list(tools.exclude(latitude=None))
        for t in tools_list:
            t.distance = haversine(float(user_lat), float(user_lng), t.latitude, t.longitude)
        tools_list.sort(key=lambda t: t.distance)
        return render(request, 'tool_list.html', {
            'tools': tools_list,
            'categories': all_categories, # Changed
        })
    elif sort == 'price_asc':
        tools = tools.order_by('daily_rate')
    elif sort == 'price_desc':
        tools = tools.order_by('-daily_rate')
    else:
        tools = tools.order_by('-created_at')

    # Paginate
    paginator = Paginator(tools, 12)
    page = request.GET.get('page')
    tools = paginator.get_page(page)

    return render(request, 'tool_list.html', {
        'tools': tools,
        'categories': all_categories, # Changed
    })

def tool_detail(request, pk):
    # prefetch_related('reviews') makes the review loop in your HTML much faster
    tool = get_object_or_404(Tool.objects.prefetch_related('reviews'), pk=pk)
    
    has_rented_before = False
    rental_id = None

    if request.user.is_authenticated:
        # Check if this specific user has ever rented this specific tool
        last_rental = tool.rentals.filter(renter=request.user).first()
        if last_rental:
            has_rented_before = True
            rental_id = last_rental.id # Useful if you want to link to a specific chat

    return render(request, 'tool_detail.html', {
        'tool': tool,
        'today': date.today(),
        'has_rented_before': has_rented_before,
        'rental_id': rental_id,
    })
from .models import Tool, Category  # ensure Category is imported

@login_required
def tool_add(request):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=request.POST.get('category'))
        tool = Tool(
            owner       = request.user,
            name        = request.POST.get('name'),
            description = request.POST.get('description'),
            category    = category,                          # ← pass object, not id string
            condition   = request.POST.get('condition'),
            daily_rate  = request.POST.get('daily_rate'),
            location    = request.POST.get('location'),
            latitude    = request.POST.get('latitude') or None,
            longitude   = request.POST.get('longitude') or None,
        )
        if request.FILES.get('image'):
            tool.image = request.FILES['image']
        tool.save()
        messages.success(request, f'"{tool.name}" listed successfully!')
        return redirect('tool_detail', pk=tool.pk)

    return render(request, 'tool_add.html', {
        'categories': Category.objects.all(),   # ← from DB, not CATEGORY_CHOICES
        'conditions': Tool.CONDITION_CHOICES,
    })


@login_required
def tool_edit(request, pk):
    tool = get_object_or_404(Tool, pk=pk, owner=request.user)
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=request.POST.get('category'))
        tool.name        = request.POST.get('name')
        tool.description = request.POST.get('description')
        tool.category    = category                          # ← pass object, not id string
        tool.condition   = request.POST.get('condition')
        tool.daily_rate  = request.POST.get('daily_rate')
        tool.location    = request.POST.get('location')
        tool.latitude    = request.POST.get('latitude') or None
        tool.longitude   = request.POST.get('longitude') or None
        if request.FILES.get('image'):
            tool.image = request.FILES['image']
        tool.save()
        messages.success(request, 'Tool updated!')
        return redirect('tool_detail', pk=tool.pk)

    return render(request, 'tool_add.html', {
        'tool'      : tool,
        'categories': Category.objects.all(),   # ← from DB, not CATEGORY_CHOICES
        'conditions': Tool.CONDITION_CHOICES,
    })


@login_required
def tool_delete(request, pk):
    tool = get_object_or_404(Tool, pk=pk, owner=request.user)
    if request.method == 'POST':
        tool.delete()
        messages.success(request, 'Tool deleted.')
        return redirect('dashboard')
    return redirect('tool_detail', pk=pk)

@login_required
def dashboard(request):
    from rentals.models import Rental
    my_tools   = Tool.objects.filter(owner=request.user)
    incoming   = Rental.objects.filter(
                     tool__owner=request.user
                 ).select_related('tool', 'renter')
    my_rentals = Rental.objects.filter(
                     renter=request.user
                 ).select_related('tool', 'tool__owner')

    # safe total earned calculation
    total_earned = 0
    for r in incoming.filter(status='returned'):
        total_earned += r.total_cost or 0

    return render(request, 'dashboard.html', {
        'my_tools':               my_tools,
        'incoming_rentals':       incoming,
        'my_rentals':             my_rentals,
        'my_tools_count':         my_tools.count(),
        'active_rentals_count':   incoming.filter(status='active').count(),
        'pending_requests_count': incoming.filter(status='pending').count(),
        'total_earned':           total_earned,
    })


