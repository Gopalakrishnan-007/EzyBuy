# Items/models.py
from django.contrib.auth.models import User
from django.db import models

class Items(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length = 80,default="c")
    

    def __str__(self):
        return self.title

class PurchasedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Item = models.ForeignKey(Items, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.Item.title}"


