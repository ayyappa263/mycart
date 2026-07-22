from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'shop'

urlpatterns = [
    #HTML Views for frontend
    path("", views.index,name='Shophome'),
    path("contact/", views.contact,name='ContactUs'),
    path('product/', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
    #API views for Javascript
    path('api/products/', views.ProductListView.as_view(), name='api_product_list'),
    path('api/products/<pk>/', views.ProductListView.as_view(), name='api_product_detail'),
    path('api/categories/', views.CategoryListView.as_view(), name='api_category_list'),
    path('api/categories/<pk>/', views.CategoryDetailView.as_view(), name='api_category_detail'),
]