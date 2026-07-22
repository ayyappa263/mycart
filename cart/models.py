from django.db import models
from shop.models import Product
# Create your models here.
class Cart(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    cart_created_date = models.DateTimeField(auto_now_add=True, null=True)
    cart_updated_date = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
