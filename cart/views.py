from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from shop.models import Product
from .models import Cart as sessioncart, CartItem
from .cart import Cart
from .forms import CartAddProductForm
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CartSerializer, CartItemSerializer
from rest_framework import generics
from .utils import get_or_create_cart
from rest_framework import viewsets
from django.conf import settings
from rest_framework.decorators import api_view

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

@api_view(['GET', 'PUT', 'PATCH'])
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity':item['quantity'], 'override':True}
        )
    return render(request, 'cart/detail.html', {
        'cart':cart
    })

class CartListView(generics.ListAPIView):
    queryset = sessioncart.objects.all()
    serializer_class = CartSerializer
    filter_backends = [DjangoFilterBackend]

class CartDetailView(generics.RetrieveAPIView):
    queryset = sessioncart.objects.all()
    serializer_class = CartSerializer

from rest_framework.response import Response
from rest_framework.decorators import action 
class CartViewSet(viewsets.ViewSet):

    def list(self, request):
        cart = get_or_create_cart(request)
        serializer_class = CartSerializer(cart)
        return Response(serializer_class.data)

    def create(self, request, pk=None):
        print("Request data:", request.data)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity':quantity})

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)

        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        quantity = request.data.get('quantity')
        cartitem_id = get_object_or_404(CartItem, id=pk)
        quantity = int(quantity)
        if quantity <= 0:
            cartitem_id.delete()
        else:
            cartitem_id.quantity = quantity
            cartitem_id.save()

        cart = cartitem_id.cart
        serializer = CartSerializer(cart)

        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        cart_item = get_object_or_404(CartItem, id=pk)
        quantity = int(request.data.get('quantity'))
        
        if quantity is None:
            return Response({'error': 'Quantity required'}, status=400)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = cart_item.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        cartitem_id = get_object_or_404(CartItem, id=pk)
        cartitem_id.delete()
        return Response(status=204)
    
    @action(detail=False, methods=['delete'])    
    def clear(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)
