from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
app_name = 'cart'
router.register(r'cart', views.CartViewSet, basename='cart')

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    # path('add/<int:product_id>', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    #API views for Javascript
    path('api/', include(router.urls)),
]