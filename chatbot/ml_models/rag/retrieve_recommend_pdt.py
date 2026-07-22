from shop.models import Product
from shop.serializers import ProductSerializer

def get_product_details(product_ids):
    if not product_ids:
        return []
    
    products = Product.objects.filter(id__in=product_ids)
    return ProductSerializer(products, many=True).data