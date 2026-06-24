# translation.py
from modeltranslation.translator import register, TranslationOptions

from .models import (
    Category, Product, Review,
    AboutUs, Contact, OpeningHours,
)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('category_name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'description')


@register(Review)
class ReviewTranslationOptions(TranslationOptions):
    fields = ('comment',)


@register(AboutUs)
class AboutUsTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Contact)
class ContactTranslationOptions(TranslationOptions):
    fields = ('address',)


@register(OpeningHours)
class OpeningHoursTranslationOptions(TranslationOptions):
    fields = ('description',)