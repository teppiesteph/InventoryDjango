from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=100)
    product_id = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    amount = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, choices=[("employee", "Employee"), ("manager", "Manager")]
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class History(models.Model):
    ACTION_CHOICES = [
        ("add", "Add"),
        ("remove", "Remove"),
        ("edit", "Edit"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    product_name = models.CharField(max_length=100)
    product_id = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    amount = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type.capitalize()} - {self.product_name} by {self.user.username}"
