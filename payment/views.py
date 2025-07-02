import paypalrestsdk
from django.shortcuts import render, redirect, get_object_or_404
from .models import Items,PurchasedItem
from django.conf import settings
from django.http import JsonResponse,HttpResponseRedirect
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q  # Import Q for complex queries



paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET_KEY,
})

@login_required
def Items_list(request):
    query = request.GET.get('q', '')  # Get search query
    price_ranges = request.GET.getlist('price_range')  # Get selected price range filters

    items = Items.objects.all()

    # Apply search filter
    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Apply price range filters
    if price_ranges:
        price_filter = Q()
        if "below_500" in price_ranges:
            price_filter |= Q(price__lt=500)
        if "500_1500" in price_ranges:
            price_filter |= Q(price__gte=500, price__lt=1500)
        if "1500_5000" in price_ranges:
            price_filter |= Q(price__gte=1500, price__lt=5000)
        if "5000_10000" in price_ranges:
            price_filter |= Q(price__gte=5000, price__lt=10000)
        if "10000_50000" in price_ranges:
            price_filter |= Q(price__gte=10000, price__lt=50000)
        if "50000_above" in price_ranges:
            price_filter |= Q(price__gte=50000)

        items = items.filter(price_filter)

    return render(request, 'Item_list.html', {
        "Items": items,
        "query": query,
        "selected_filters": price_ranges,
    })

@login_required
def Item_detail(request, Item_id):
    Item = get_object_or_404(Items, id=Item_id)
    return render(request, 'Item_detail.html', {'Item': Item, 'CLIENT_ID': settings.PAYPAL_CLIENT_ID})

def create_order(request, Item_id):
    """View to handle PayPal order creation"""
    Item = get_object_or_404(Items, id=Item_id)
    
    # Create the PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(f'/Items/{Item_id}/payment-success'),
            "cancel_url": request.build_absolute_uri(f'/Items/{Item_id}/payment-cancel')
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": Item.title,
                    "sku": Item.id,
                    "price": str(Item.price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(Item.price),
                "currency": "USD"
            },
            "description": f"Purchase of {Item.title}."
        }]
    })
    
    if payment.create():
        # Redirect user to PayPal for payment approval
        for link in payment.links:
            if link.rel == "approval_url":
                return JsonResponse({'approval_url': link.href})  # Return the approval URL as JSON
    else:
        # Handle payment creation failure
        return JsonResponse({'error': payment.error}, status=400)


@login_required
def payment_success(request, Item_id):
    """View to handle successful PayPal payments"""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    # Find the payment using PayPal SDK
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        # Payment was successful
        item = get_object_or_404(Items, id=Item_id)
        
        # Add the purchased item to the PurchasedItem model
        PurchasedItem.objects.create(user=request.user, item=item)
        
        return render(request, 'payment_success.html', {'payment': payment})
    else:
        # Handle payment execution failure
        return JsonResponse({'error': payment.error}, status=400)





def payment_cancel(request, Item_id):
    """View to handle payment cancellation"""
    return render(request, 'payment_cancel.html')












def register(request):
    form = RegistrationForm();
    if request.method == 'POST':
        username = request.POST.get('username')  # Use `get` to avoid KeyError
        email = request.POST.get('email')
        fn = request.POST.get('first_name')
        ln = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered!")
            else:
                # Create a new user
                user = User.objects.create_user(username=username,first_name=fn,last_name=ln,email=email, password=password1)
                user.save()
                messages.success(request, "Account created successfully!")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match!")

    return render(request, 'register.html',{'form':form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('Items_list')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    purchased_items = PurchasedItem.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'purchased_items': purchased_items})


