from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Product, History
from .forms import CustomSignupForm
from django.contrib.messages import get_messages
import json


# Helper functions to check user roles
def is_manager(user):
    return user.groups.filter(name="manager").exists()


def is_employee(user):
    return user.groups.filter(name="employee").exists()


# Login view
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "inventory/login.html", {"form": form})


# Landing page view
def landing_page(request):
    return render(request, "inventory/landing_page.html")


# Dashboard view
@login_required
def dashboard(request):
    username = request.user.username
    role = "Manager" if is_manager(request.user) else "Employee"
    return render(request, "inventory/dashboard.html", {"username": username, "role": role})


# About Us page view
def about_page(request):
    return render(request, "inventory/about.html")


# Contact page view
def contact_page(request):
    return render(request, "inventory/contact.html")


# Signup view
def signup(request):
    storage = get_messages(request)  # Clear existing messages
    for _ in storage:
        pass

    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        role = request.POST.get("role")
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            if role not in ["manager", "employee"]:
                messages.error(request, "Please select a valid role: Manager or Employee.")
                return render(request, "inventory/signup.html", {"form": form})
            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            group_name = "manager" if role == "manager" else "employee"
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            messages.success(request, f"Account for '{username}' created successfully! You can now log in.")
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomSignupForm()
    return render(request, "inventory/signup.html", {"form": form})


# Add product view
@login_required
@user_passes_test(is_manager, login_url="dashboard")
def add_product(request):
    if request.method == "POST":
        name = request.POST["name"]
        product_id = request.POST["product_id"]
        description = request.POST["description"]
        amount = request.POST["amount"]
        location = request.POST["location"]

        if Product.objects.filter(product_id=product_id).exists():
            messages.error(request, f"Product ID '{product_id}' already exists.")
            return redirect("add_product")

        product = Product.objects.create(
            name=name, product_id=product_id, description=description, amount=amount, location=location
        )
        History.objects.create(
            user=request.user,
            action_type="add",
            product_name=name,
            product_id=product_id,
            description=description,
            amount=amount,
            location=location,
        )
        messages.success(request, f"Product '{name}' added successfully.")
        return redirect("dashboard")
    return render(request, "inventory/add_product.html")


# Remove product view
@login_required
@user_passes_test(is_manager, login_url="dashboard")
def remove_product(request):
    products = Product.objects.all()
    if request.method == "POST":
        product_id = request.POST["product_id"]
        try:
            product = Product.objects.get(product_id=product_id)
            History.objects.create(
                user=request.user,
                action_type="remove",
                product_name=product.name,
                product_id=product.product_id,
                description=product.description,
                amount=product.amount,
                location=product.location,
            )
            product.delete()
            messages.success(request, f"Product '{product.name}' removed.")
            return redirect("remove_product")
        except Product.DoesNotExist:
            messages.error(request, f"Product ID '{product_id}' not found.")
    return render(request, "inventory/remove_product.html", {"products": products})


# Edit product view
@login_required
@user_passes_test(is_manager, login_url="dashboard")
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        name = request.POST["name"]
        new_product_id = request.POST["product_id"]
        description = request.POST["description"]
        amount = request.POST["amount"]
        location = request.POST["location"]

        if Product.objects.filter(Q(product_id=new_product_id) & ~Q(id=product.id)).exists():
            messages.error(request, f"Product ID '{new_product_id}' is already in use.")
            return redirect("edit_product", product_id=product.id)

        product.name = name
        product.product_id = new_product_id
        product.description = description
        product.amount = amount
        product.location = location
        product.save()

        History.objects.create(
            user=request.user,
            action_type="edit",
            product_name=name,
            product_id=new_product_id,
            description=description,
            amount=amount,
            location=location,
        )
        messages.success(request, f"Product '{name}' updated successfully.")
        return redirect("view_products")
    return render(request, "inventory/edit_product.html", {"product": product})


# Upload inventory view
@login_required
@user_passes_test(is_manager, login_url="dashboard")
def upload_inventory(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("inventory_file")
        if not uploaded_file.name.endswith(".txt"):
            messages.error(request, "Only .txt files are supported.")
            return redirect("dashboard")

        try:
            decoded_file = uploaded_file.read().decode("utf-8").splitlines()
            with transaction.atomic():
                for line in decoded_file:
                    name, product_id, description, amount, location = line.split(",")
                    amount = int(amount)
                    product, created = Product.objects.get_or_create(
                        product_id=product_id.strip(),
                        defaults={
                            "name": name.strip(),
                            "description": description.strip(),
                            "amount": amount,
                            "location": location.strip(),
                        },
                    )
                    if not created:
                        product.amount += amount
                        product.save()
            messages.success(request, "Inventory uploaded and updated successfully.")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
        return redirect("dashboard")
    return render(request, "inventory/upload_inventory.html")


# Undo last action view
@login_required
@user_passes_test(is_manager, login_url="dashboard")
def undo_last_action(request):
    last_action = History.objects.filter(user=request.user).order_by("-timestamp").first()
    if not last_action:
        messages.error(request, "No actions to undo.")
        return redirect("dashboard")

    if last_action.action_type == "add":
        Product.objects.filter(product_id=last_action.product_id).delete()
    elif last_action.action_type == "remove":
        Product.objects.create(
            name=last_action.product_name,
            product_id=last_action.product_id,
            description=last_action.description,
            amount=last_action.amount,
            location=last_action.location,
        )
    elif last_action.action_type == "edit":
        product = Product.objects.get(product_id=last_action.product_id)
        product.name = last_action.product_name
        product.description = last_action.description
        product.amount = last_action.amount
        product.location = last_action.location
        product.save()

    last_action.delete()
    messages.success(request, "Last action undone successfully.")
    return redirect("dashboard")


# View products view
@login_required
def view_products(request):
    products = Product.objects.all()
    return render(request, "inventory/view_products.html", {"products": products})


# Search products view
@login_required
def search_products(request):
    query = request.GET.get("query", "")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, "inventory/search_products.html", {"products": products, "query": query})


# Signal to limit history to 10 actions per user
@receiver(post_save, sender=History)
def limit_history(sender, instance, **kwargs):
    history_count = History.objects.filter(user=instance.user).count()
    if history_count > 10:
        excess_actions = History.objects.filter(user=instance.user).order_by("timestamp")[: history_count - 10]
        excess_actions.delete()
