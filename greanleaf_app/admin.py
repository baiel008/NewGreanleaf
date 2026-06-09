from django.contrib import admin
from .models import *


admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PurchaseArchive)
admin.site.register(AboutUs)
admin.site.register(Contact)