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

# store user role
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    role = models.CharField(max_length=10, choices=[('employee', 'Employee'), ('manager', 'Manager')])

    def __str__(self):
        return f"{self.user.username} - {self.role}"
