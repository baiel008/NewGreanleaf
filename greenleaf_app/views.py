from rest_framework import generics, status, viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from .serializers import VerifyResetCodeSerializer  # Убедись, что путь правильный


@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔐 РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
class RegisterView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)   # Получаем сериализатор с входными данными
        serializer.is_valid(raise_exception=True)                    # Проверяет ошибку если не правильно
        user = serializer.save()                                                          # Сохраняем пользователя (должен быть вызов create_user внутри сериализатора!)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 🔐 КАСТОМНЫЙ ЛОГИН С JWT
class CustomLoginView(TokenObtainPairView):             # Наследование TokenObtainPairView алып атат
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)   # Получаем сериализатор с логин-данными
        try:
            serializer.is_valid(raise_exception=True)                # Пробуем валидировать
        except Exception:
            return Response({'detail': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data                                         # Здесь — уже валидные данные и токены
        return Response(serializer.data, status=status.HTTP_200_OK)

# 🔐 ВЫХОД ИЗ СИСТЕМЫ (ОТЗЫВ refresh-токена)
class LogoutView(generics.GenericAPIView):                     # GenericAPIView, потому что не нужен CRUD, только POST
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data['refresh']                       # Получаем refresh токен из тела запроса
            token = RefreshToken(refresh_token)                        # Оборачиваем в специальный объект токена
            token.blacklist()  # Помещаем токен в чёрный список (требуется настройка!)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# ─── UserProfile ───────────────────────────────────────────────────────────────

class UserProfileListAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListSerializer


class UserProfileDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer


# ─── Category ──────────────────────────────────────────────────────────────────

class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ─── Product ───────────────────────────────────────────────────────────────────

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


# ─── ProductImage ──────────────────────────────────────────────────────────────

class ProductImageListCreateAPIView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductImageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


# ─── Favorite ──────────────────────────────────────────────────────────────────

class FavoriteListCreateAPIView(generics.ListCreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class FavoriteDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


# ─── Cart ──────────────────────────────────────────────────────────────────────

class CartListCreateAPIView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


# ─── CartItem ──────────────────────────────────────────────────────────────────

class CartItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class CartItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


# ─── Order ─────────────────────────────────────────────────────────────────────

class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(serializer.to_representation(order), status=status.HTTP_201_CREATED)


class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer


# ─── OrderItem ─────────────────────────────────────────────────────────────────

class OrderItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


# ─── PurchaseArchive ───────────────────────────────────────────────────────────

class PurchaseArchiveListAPIView(generics.ListCreateAPIView):
    serializer_class = PurchaseArchiveSerializer

    def get_queryset(self):
        # каждый видит только свой архив
        return PurchaseArchive.objects.filter(
            user=self.request.user
        ).select_related('product', 'order').order_by('-created_at')


class PurchaseArchiveDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseArchiveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PurchaseArchive.objects.filter(user=self.request.user)


# ─── AboutUs ───────────────────────────────────────────────────────────────────

class AboutUsListCreateAPIView(generics.ListCreateAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer


class AboutUsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer


# class AboutAsImgView(viewsets.ModelViewSet):
#     queryset = AboutAsImg.obj.all()
#     serializer_class = AboutAsImgSerializer
#

# ─── Contact ───────────────────────────────────────────────────────────────────

class ContactListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

# ─── OpeningHours ───────────────────────────────────────────────────────────────────
class OpeningHoursListAPIView(generics.ListAPIView):
    queryset = OpeningHours.objects.all()
    serializer_class = OpeningHoursListSerializers


class OpeningHoursDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OpeningHours.objects.all()
    serializer_class = OpeningHoursListSerializers