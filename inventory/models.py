from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    product_id = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    amount = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name
