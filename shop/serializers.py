from rest_framework import serializers
from .models import Product, master_Category

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'master_Category', 'sub_Category', 'article_Type', 'colour', 'usage','slug', 'price', 'image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = master_Category
        fields = ['name', 'slug']