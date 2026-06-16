from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Avg
from multiselectfield import MultiSelectField



class UserProfile(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('seller', 'seller'),
        ('client', 'client')
    )
    user_role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

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

    @property
    def avg_rating(self):
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    def get_count_rating(self):
        count = self.reviews.count()
        return '500+' if count > 500 else count

    @property
    def good_rate(self):
        total = self.reviews.count()
        if total == 0:
            return '0%'
        good = self.reviews.filter(rating__gt=3).count()
        return f'{round((good * 100) / total)}%'

    def __str__(self):
        return f'{self.product_name}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f'{self.product.product_name}'

class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)



    def is_reply(self):
        return self.parent is not None

    @property
    def likes_count(self):
        return self.likes.count()

    def __str__(self):
        if self.is_reply():
            return f"Reply by {self.user.username} to Review {self.parent.id}"
        return f"Review by {self.user.username} on {self.product.product_name}"

class CommentLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f'{self.user} - {self.review}'

class Favorite(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='favorite')

    def __str__(self):
        return f'{self.user}'

class FavoriteProducts(models.Model):
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('favorite', 'product')

    def __str__(self):
        return f'{self.favorite.user} — {self.product.product_name}'


class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    session_id = models.CharField(max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart #{self.session_id}'

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.product_name} x{self.quantity}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_product'
            )
        ]


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

    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=20)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=64, blank=True)
    email = models.EmailField()
    comment = models.TextField(blank=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup')
    region = models.CharField(max_length=150)
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


class PurchaseArchive(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='archive')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='archived_by')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='archive')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} — {self.product.product_name}'


class AboutUs(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'

class AboutAsImg(models.Model):
    about = models.ForeignKey(AboutUs, on_delete=models.CASCADE, related_name='about_images')
    image = models.ImageField(upload_to='about_images/')

    def __str__(self):
        return f'{self.about.title}'


class Contact(models.Model):
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    instagram = models.CharField(max_length=200, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.phone_number}'

class OpeningHours(models.Model):
    DAY_CHOICES = (
        ('ПН', 'ПН'),
        ('ВТ', 'ВТ'),
        ('СР', 'СР'),
        ('ЧТ', 'ЧТ'),
        ('ПТ', 'ПТ'),
        ('СБ', 'СБ'),
        ('ВС', 'ВС'),
    )
    work_day = MultiSelectField(choices=DAY_CHOICES, max_choices=7)
    data = models.DateField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.description}'
