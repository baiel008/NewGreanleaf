from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField



class UserProfile(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'



class Category(models.Model):
    category_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.category_name}'


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    article_number = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pv = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.product_name}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f'{self.product.product_name}'


class Cart(models.Model):
    session_id = models.CharField(max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart #{self.session_id}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.product_name} x{self.quantity}'


class Order(models.Model):
    DELIVERY_CHOICES = (
        ('pickup', 'Самовывоз'),
        ('yandex', 'Яндекс'),
    )

    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждён'),
        ('cancelled', 'Отменён'),
    )
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=20)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=64, blank=True)
    email = models.EmailField()
    comment = models.TextField(blank=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup')
    street = models.CharField(max_length=128, blank=True)
    house = models.CharField(max_length=32, blank=True)
    apartment = models.CharField(max_length=32, blank=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} — {self.last_name} {self.first_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.product_name} x{self.quantity}'