from rest_framework import serializers
from .models import Cart, CartItem
from shop.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'items', 'session_key', 'item_count', 'total']

    def get_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    
    def get_item_count(self, obj):
        return sum(item.quantity for item in obj.items.all())

