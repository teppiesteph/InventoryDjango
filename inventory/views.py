from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Product
import json

def landing_page(request):
    print("Landing page view accessed")  # Add this line for debugging
    return render(request, 'inventory/landing_page.html')
# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'inventory/signup.html', {'form': form})

# Dashboard view
@login_required
def dashboard(request):
    return render(request, 'inventory/dashboard.html')

# Add product view
@login_required
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

# Remove product view
@login_required
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

