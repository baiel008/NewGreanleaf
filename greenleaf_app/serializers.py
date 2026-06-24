from django.db.models import Sum, F
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken  # Класс для создания access и refresh токенов
from django.contrib.auth import authenticate  # Функция, которая проверяет логин и пароль
from django.core.mail import send_mail
from django_rest_passwordreset.models import ResetPasswordToken
from django.contrib.auth import get_user_model

User = get_user_model()

class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают.")

        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=str(reset_code))
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        data['token'] = token
        return data

    def save(self):
        user = self.validated_data['user']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        # Удаляем использованный токен
        token.delete()


# ─── Register ──────────────────────────────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password', 'first_name', 'last_name',
                  'phone_number')  # Указываем, какие поля включить
        extra_kwargs = {
            'password': {'write_only': True}}  # Пароль не должен отображаться при выводе данных (пороль не будет видно)

    def create(self, validated_data):  # create авоматически хеширует пороль
        user = UserProfile.objects.create_user(**validated_data)  # Используем встроенный метод для создания пользователя
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # Поле для логина
    password = serializers.CharField(write_only=True)  # Пароль — только на запись (чыгарып бербейт поролду кайра)

    def validate(self, data):
        user = authenticate(**data)  # Проверка логина и пароля
        if user and user.is_active:  # Если пользователь найден и активен
            return user  # Возвращаем объект пользователя
        raise serializers.ValidationError('Неверные учетные данные')  # Ошибка при неверном логине/пароле

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)  # Создаём refresh токен
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),  # access токен — для авторизации
            'refresh': str(refresh),  # refresh токен — для обновления access токена
        }



# ─── PurchaseArchive ──────────────────────────────────────────────────────────────
class PurchaseArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseArchive
        fields = ['id', 'user', 'product', 'order', 'created_at']


# ─── OrderItem ──────────────────────────────────────────────────────────────
class OrderItemSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price', 'total']


    def get_total(self, obj):
        return obj.price * obj.quantity


# ─── Order ──────────────────────────────────────────────────────────────
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    archive = PurchaseArchiveSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    cart_id = serializers.IntegerField(write_only=True)  # ← добавить сюда
    class Meta:
        model = Order
        fields = ['id', 'user', 'first_name', 'last_name', 'phone_number', 'is_paid',
                  'payment_id', 'email', 'comment', 'delivery_type', 'region', 'street', 'house',
                  'apartment', 'order_status', 'created_at', 'items', 'archive', 'total_price', 'cart_id']
        read_only_fields = ['user', 'is_paid', 'payment_id', 'order_status', 'created_at']


    def validate_cart_id(self, value):
        try:
            cart = Cart.objects.prefetch_related('items__product').get(id=value)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Корзина не найдена")

        if not cart.items.exists():
            raise serializers.ValidationError("Корзина пуста")

        self._cart = cart
        return value

    def create(self, validated_data):
        validated_data.pop('cart_id')
        cart = self._cart
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None

        order = Order.objects.create(user=user, **validated_data)

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,  # фиксируем цену на момент покупки
            )
            for item in cart.items.all()
        ]
        OrderItem.objects.bulk_create(order_items)
        # 2️⃣ Добавляем каждый товар в архив покупок (если пользователь авторизован)
        if user:
            archive_entries = [
                PurchaseArchive(
                    user=user,
                    product=item.product,
                    order=order,
                )
                for item in cart.items.all()
            ]
            PurchaseArchive.objects.bulk_create(archive_entries)

        # 3️⃣ Очищаем корзину
        cart.items.all().delete()

        return order


    def get_total_price(self, obj):
        return obj.items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0

    def validate(self, data):
        if data.get('delivery_type') == 'yandex':
            if not data.get('region'):
                raise serializers.ValidationError({'region': 'Укажите регион'})
            if not data.get('street'):
                raise serializers.ValidationError({'street': 'Укажите улицу'})
            if not data.get('house'):
                raise serializers.ValidationError({'house': 'Укажите дом'})
        return data

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

# ─── UserProfile ──────────────────────────────────────────────────────────────
class UserProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email','user_role']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    archive = PurchaseArchiveSerializer(many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'orders', 'archive','user_role']


# ─── UserProfileReview ──────────────────────────────────────────────────────────────
class UserProfileReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id','username')


# ─── Product ──────────────────────────────────────────────────────────────
class ProductMiniSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product_name')

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# ─── ProductImage ──────────────────────────────────────────────────────────────
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


# ─── ReviewReply ──────────────────────────────────────────────────────────────
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


# ─── Review ──────────────────────────────────────────────────────────────
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


# ─── Product ──────────────────────────────────────────────────────────────
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


# ─── ProductCreate ──────────────────────────────────────────────────────────────
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



# ─── CartItem ──────────────────────────────────────────────────────────────
class CartItemSerializer(serializers.ModelSerializer):
    # ✅ добавили вложенный товар — фронт должен знать что за товар в корзине
    product = ProductListSerializer(read_only=True)
    # ✅ product_id для записи — чтобы можно было добавить товар в корзину по id
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity', 'total']

    def get_total(self, obj):
        return obj.product.price * obj.quantity


# ─── Cart ──────────────────────────────────────────────────────────────
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.items.aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0


# ─── Category ──────────────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'products']


# ─── AboutUs ──────────────────────────────────────────────────────────────
class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ['id', 'title', 'description', 'created_at']


class AboutAsImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutAsImg
        fields = '__all__'


# ─── Contact ──────────────────────────────────────────────────────────────
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'phone_number', 'email', 'address', 'instagram', 'whatsapp']


# ─── Favorite ──────────────────────────────────────────────────────────────
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['favorite']


# ─── FavoriteProducts ──────────────────────────────────────────────────────────────
class FavoriteProductSerializer(serializers.ModelSerializer):
    fav_product = FavoriteSerializer(many=True, read_only=True)
    class Meta:
        model = FavoriteProducts
        fields = ['id', 'fav_product', 'product', 'created_at']

class OpeningHoursListSerializers(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ['id', 'data', 'work_day', 'description']


