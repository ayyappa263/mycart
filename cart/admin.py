from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'cart_created_date', 'cart_updated_date']
    search_fields = ['session_key']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id','cart', 'product', 'quantity']
    list_filter = ['cart', 'product']
