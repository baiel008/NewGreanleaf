from rest_framework import serializers
from .models import *


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
    orders = OrderSerializer(many=True, read_only=True)
    archive = PurchaseArchiveSerializer(many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'orders', 'archive']

# class ProductDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class UserProfileReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id','username')

class ProductMiniSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product_name')

class ReviewReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    parent_user_name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = (
            'id',
            'user_name',
            'comment',
            'rating',
            'likes_count',
            'parent_user_name',
        )


    def get_parent_user_name(self, obj):
        if obj.parent:
            return obj.parent.user.username  # вот так берём имя родителя
        return None




class ReviewSerializers(serializers.ModelSerializer):
    user_reviews = UserProfileReviewSerializers(source='user', read_only=True)
    likes_count = serializers.ReadOnlyField()
    replies = serializers.SerializerMethodField()
    product   = ProductMiniSerializers(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'user_reviews', 'product', 'rating', 'comment',
                  'created_at', 'likes_count', 'replies', 'parent', 'product_id')


    def get_replies(self, obj):
        qs = obj.replies.all()
        return ReviewReplySerializer(qs, many=True).data



class ReviewDetailSerializers(serializers.ModelSerializer):
    user_reviews = UserProfileReviewSerializers(source='user', read_only=True)
    likes_count = serializers.ReadOnlyField()
    replies = serializers.SerializerMethodField()  # вложенные ответы

    class Meta:
        model = Review
        fields = ('id', 'user_reviews', 'product', 'rating', 'comment',
                  'likes_count', 'created_at', 'replies', 'parent')
        read_only_fields = ['user', 'likes_count', 'created_at']

    def get_replies(self, obj):
        qs = obj.replies.all()
        return ReviewReplySerializer(qs, many=True).data




class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    count_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'article_number', 'price', 'pv', 'images', 'avg_rating', 'count_rating']

    def get_avg_rating(self, obj):
            return obj.avg_rating

    def get_count_rating(self, obj):
            return obj.get_count_rating()




class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # ❌ убрали favorited_by — утечка: любой видит всех кто лайкнул товар
    # ❌ убрали cart_items   — утечка: любой видит чужие корзины
    # ❌ убрали order_items  — утечка: любой видит чужие заказы
    # ❌ убрали archived_by  — утечка: любой видит историю покупок других
    similar_products = serializers.SerializerMethodField()  # похожие товары

    def get_similar_products(self, obj):
        # берём товары из той же категории, исключаем текущий, максимум 6
        products = Product.objects.filter(
            category=obj.category,
            is_available=True
        ).exclude(id=obj.id)[:6]
        return ProductListSerializer(products, many=True).data

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'article_number', 'description',
                  'price', 'pv', 'is_available', 'created_at', 'category', 'images', 'similar_products']



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


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['favorite']


class FavoriteProductSerializer(serializers.ModelSerializer):
    fav_product = FavoriteSerializer(many=True, read_only=True)
    class Meta:
        model = FavoriteProducts
        fields = ['id', 'user', 'fav_product']