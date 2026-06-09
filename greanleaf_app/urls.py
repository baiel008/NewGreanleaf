from .views import *
from django.urls import path, include
from rest_framework import routers


router = routers.DefaultRouter()

router.register(r'category', CategoryViewSet, basename='category_list')
router.register(r'product', ProductViewSet, basename='product_list')
router.register(r'product-image', ProductImageViewSet, basename='product_image_list')

router.register(r'cart', CartViewSet, basename='cart_list')
router.register(r'cart-item', CartItemViewSet, basename='cart_item_list')

router.register(r'order', OrderViewSet, basename='order_list')
router.register(r'order-item', OrderItemViewSet, basename='order_item_list')


urlpatterns = [
    path('', include(router.urls)),
]