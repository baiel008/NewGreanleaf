from rest_framework import serializers
from .models import *

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']


class PurchaseArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseArchive
        fields = ['id', 'user', 'product', 'order', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    archive = PurchaseArchiveSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'first_name', 'last_name', 'phone_number', 'is_paid',
                  'payment_id', 'email', 'comment', 'delivery_type', 'street', 'house',
                  'apartment', 'order_status', 'created_at', 'items', 'archive']


class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    favorites = FavoriteSerializer(many=True, read_only=True)
    orders = OrderSerializer(many=True, read_only=True)
    archive = PurchaseArchiveSerializer(many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'favorites', 'orders', 'archive']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'article_number', 'price', 'pv', 'images']


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # ❌ убрали favorited_by — утечка: любой видит всех кто лайкнул товар
    # ❌ убрали cart_items   — утечка: любой видит чужие корзины
    # ❌ убрали order_items  — утечка: любой видит чужие заказы
    # ❌ убрали archived_by  — утечка: любой видит историю покупок других

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'article_number', 'description',
                  'price', 'pv', 'is_available', 'created_at', 'category', 'images']



class CartItemSerializer(serializers.ModelSerializer):
    # ✅ добавили вложенный товар — фронт должен знать что за товар в корзине
    product = ProductListSerializer(read_only=True)
    # ✅ product_id для записи — чтобы можно было добавить товар в корзину по id
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'items']


class CategorySerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'products']


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ['id', 'title', 'description', 'created_at']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'phone_number', 'email', 'address', 'instagram', 'whatsapp']