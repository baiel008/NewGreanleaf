# from .views import *
# from django.urls import path, include
# from rest_framework import routers
#
#
# router = routers.DefaultRouter()
#
# router.register(r'user', UserProfileViewSet, basename='user_list')
#
# router.register(r'category', CategoryViewSet, basename='category_list')
# router.register(r'product', ProductViewSet, basename='product_list')
# router.register(r'product-image', ProductImageViewSet, basename='product_image_list')
#
# router.register(r'favorite', FavoriteViewSet, basename='favorite_list')
#
# router.register(r'cart', CartViewSet, basename='cart_list')
# router.register(r'cart-item', CartItemViewSet, basename='cart_item_list')
#
# router.register(r'order', OrderViewSet, basename='order_list')
# router.register(r'order-item', OrderItemViewSet, basename='order_item_list')
#
#
# router.register(r'archive', PurchaseArchiveViewSet, basename='archive')
# router.register(r'about', AboutUsViewSet, basename='about')
# router.register(r'contact', ContactViewSet, basename='contact')
#
# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path
from .views import *


urlpatterns = [
    # ─── UserProfile ───────────────────────────────────────────────────────────
    path('users/', UserProfileListAPIView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserProfileDetailAPIView.as_view(), name='user_detail'),

    # ─── Category ──────────────────────────────────────────────────────────────
    path('categories/', CategoryListCreateAPIView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),

    # ─── Product ───────────────────────────────────────────────────────────────
    path('products/', ProductListAPIView.as_view(), name='product_list'),
    path('products/create/', ProductCreateAPIView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),

    # ─── ProductImage ──────────────────────────────────────────────────────────
    path('product_images/', ProductImageListCreateAPIView.as_view(), name='product_image_list'),
    path('product_images/<int:pk>/', ProductImageDetailAPIView.as_view(), name='product_image_detail'),

    # ─── Favorite ──────────────────────────────────────────────────────────────
    path('favorites/', FavoriteListCreateAPIView.as_view(), name='favorite_list'),
    path('favorites/<int:pk>/', FavoriteDetailAPIView.as_view(), name='favorite_detail'),

    # ─── Cart ──────────────────────────────────────────────────────────────────
    path('carts/', CartListCreateAPIView.as_view(), name='cart_list'),
    path('carts/<int:pk>/', CartDetailAPIView.as_view(), name='cart_detail'),

    # ─── CartItem ──────────────────────────────────────────────────────────────
    path('cart_items/', CartItemListCreateAPIView.as_view(), name='cart_item_list'),
    path('cart_items/<int:pk>/', CartItemDetailAPIView.as_view(), name='cart_item_detail'),

    # ─── Order ─────────────────────────────────────────────────────────────────
    path('orders/', OrderListCreateAPIView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order_detail'),

    # ─── OrderItem ─────────────────────────────────────────────────────────────
    path('order_items/', OrderItemListCreateAPIView.as_view(), name='order_item_list'),
    path('order_items/<int:pk>/', OrderItemDetailAPIView.as_view(), name='order_item_detail'),

    # ─── PurchaseArchive ───────────────────────────────────────────────────────
    path('archive/', PurchaseArchiveListAPIView.as_view(), name='archive_list'),
    path('archive/<int:pk>/', PurchaseArchiveDetailAPIView.as_view(), name='archive_detail'),

    # ─── AboutUs ───────────────────────────────────────────────────────────────
    path('about/', AboutUsListCreateAPIView.as_view(), name='about_list'),
    path('about/<int:pk>/', AboutUsDetailAPIView.as_view(), name='about_detail'),

    # ─── Contact ───────────────────────────────────────────────────────────────
    path('contacts/', ContactListCreateAPIView.as_view(), name='contact_list'),
    path('contacts/<int:pk>/', ContactDetailAPIView.as_view(), name='contact_detail'),
]