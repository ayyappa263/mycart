from rest_framework import serializers
from shop.models import Product
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):

    products = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'session_id',
            'message',
            'role',
            'recommended_product',
            'user_image',
            'rag_context',
            'product_ids',
            'products'
        ]

    def get_products(self, obj):

        if not obj.product_ids:
            return []

        products = Product.objects.filter(id__in=obj.product_ids)

        product_map = {
            product.id: product
            for product in products
        }

        result = []

        for pid in obj.product_ids:
            product = product_map.get(pid)

            if product:
                result.append({
                    "id": product.id,
                    "product_name": product.product_name,
                    "price": product.price,
                    "image": product.image.url if product.image else None,
                })

        return result
