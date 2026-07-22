from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import master_Category, Product, Contact, Orders
from math import ceil
from cart.forms import CartAddProductForm
from django.http import JsonResponse
from rest_framework import generics
from .serializers import ProductSerializer, CategorySerializer
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser
from chatbot.ml_models.recommender_sys.recommender_system import ALSRecommender

recommender = ALSRecommender()

def index(request):
    session_id = request.session.session_key
    recommended_products = []

    if session_id:
        try:
            product_ids = recommender.recommend_for_user(user_id=session_id,top_n=8)

            if product_ids:
                recommended_products = list(Product.objects.filter(id__in=product_ids))

        except Exception as e:
            print(f"ALS Error: {e}")

    if not recommended_products:
        recommended_products = list(Product.objects.order_by('-created_date')[:8])

    recommended_slides = [recommended_products[i:i + 4] for i in range(0, len(recommended_products), 4)]

    category_products = {}

    categories = master_Category.objects.all()[:5]

    for category in categories:
        category_products[category.name] = Product.objects.filter(master_Category=category)[:4]

    context = {'recommended_products': recommended_slides,'category_products': category_products}

    return render(request,'shop/index.html',context)

def product_list(request, category_slug=None):
    category = None
    categories = master_Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(master_Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {'category':category,'categories':categories,'products':products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    cart_product_form = CartAddProductForm()

    return render(request, 'shop/product/detail.html', {
        'product':product, 'cart_product_form':cart_product_form
    })

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['master_Category','price']

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    parser_classes = [MultiPartParser, FormParser]
    filterset_class = ProductFilter
    search_fields = ['product_name']

    def get_queryset(self):
        pk = self.kwargs.get('pk') 
        if pk:
            id_list = [i for i in pk.split(',') if i.strip().isdigit()]
            return Product.objects.filter(id__in=id_list)
        return Product.objects.all()

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryListView(generics.ListAPIView):
    queryset = master_Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = master_Category.objects.all()
    serializer_class = CategorySerializer

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name',"")
        email = request.POST.get('email',"")
        phone = request.POST.get('phone',"")
        desc = request.POST.get('desc',"")
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
    
    return render(request, 'shop/contact.html')
