from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Product
from .forms import CustomSignupForm  
from django.contrib.auth.models import Group
import json

# Helper functions to check user roles
def is_manager(user):
    return user.groups.filter(name='manager').exists()

def is_employee(user):
    return user.groups.filter(name='employee').exists()

# Login view
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'inventory/login.html', {'form': form})

# Landing page view
def landing_page(request):
    print("Landing page view accessed")  # Debugging line
    return render(request, 'inventory/landing_page.html')

# Signup view with role selection
def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            user.save()

            # Assign user to a group based on selected role
            group_name = 'manager' if role == 'manager' else 'employee'
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            # Log the user in
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomSignupForm()
    return render(request, 'inventory/signup.html', {'form': form})

# Dashboard view 
@login_required
def dashboard(request):
    return render(request, 'inventory/dashboard.html')

# Add product view (restricted to managers only)
@login_required
@user_passes_test(is_manager, login_url='dashboard')
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        product_id = request.POST['product_id']
        description = request.POST['description']
        amount = request.POST['amount']
        location = request.POST['location']

        # Create and save product
        product = Product(name=name, product_id=product_id, description=description, amount=amount, location=location)
        product.save()

        # Log the addition
        with open('transactions.log', 'a') as log_file:
            log_file.write(f"Product added: {product.name}, by {request.user.username}\n")

        # Save to JSON
        products = list(Product.objects.values())
        with open('products.json', 'w') as json_file:
            json.dump(products, json_file)

        return redirect('dashboard')

    return render(request, 'inventory/add_product.html')

# Remove product view (restricted to managers only)
@login_required
@user_passes_test(is_manager, login_url='dashboard')
def remove_product(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        try:
            product = Product.objects.get(product_id=product_id)
            product.delete()

            # Log the removal
            with open('transactions.log', 'a') as log_file:
                log_file.write(f"Product removed: {product_id}, by {request.user.username}\n")

            return redirect('dashboard')
        except Product.DoesNotExist:
            return render(request, 'inventory/remove_product.html', {'error': 'Product not found.'})

    return render(request, 'inventory/remove_product.html')

# View products view 
@login_required
def view_products(request):
    products = Product.objects.all()
    return render(request, 'inventory/view_products.html', {'products': products})
