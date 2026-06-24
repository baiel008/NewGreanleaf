# admin.py
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    UserProfile, Category, Product, ProductImage,
    Review, CommentLike, Favorite, FavoriteProducts,
    Cart, CartItem, Order, OrderItem,
    PurchaseArchive, AboutUs, AboutAsImg, Contact, OpeningHours,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class AboutAsImgInline(admin.TabularInline):
    model = AboutAsImg
    extra = 1


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class FavoriteProductsInline(admin.TabularInline):
    model = FavoriteProducts
    extra = 1


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    inlines = (ProductImageInline,)
    list_display = ('product_name', 'article_number', 'price', 'pv', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('product_name', 'article_number')
    list_editable = ('is_available',)
    list_per_page = 50

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Review)
class ReviewAdmin(TranslationAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__product_name')

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    inlines = (FavoriteProductsInline,)
    list_display = ('user',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = (CartItemInline,)
    list_display = ('session_id', 'user', 'created_at')
    search_fields = ('session_id',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = ('id', 'last_name', 'first_name', 'phone_number', 'delivery_type', 'order_status', 'is_paid', 'created_at')
    list_filter = ('order_status', 'delivery_type', 'is_paid')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_editable = ('order_status',)
    list_per_page = 50


@admin.register(PurchaseArchive)
class PurchaseArchiveAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'order', 'created_at')
    search_fields = ('user__username', 'product__product_name')


@admin.register(AboutUs)
class AboutUsAdmin(TranslationAdmin):
    inlines = (AboutAsImgInline,)
    list_display = ('title', 'created_at')

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Contact)
class ContactAdmin(TranslationAdmin):
    list_display = ('phone_number', 'email', 'address')

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(OpeningHours)
class OpeningHoursAdmin(TranslationAdmin):
    list_display = ('work_day', 'data', 'description')

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.24/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')