from django.contrib import admin
from .models import Wishlist,CartItem

# Register your models here.
admin.site.register(Wishlist)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')  # Display fields in the admin list view
    list_filter = ('user',)  # Allow filtering by user
    search_fields = ('user__username', 'product__name')  # Add search functionality by user and product

admin.site.register(CartItem, CartItemAdmin)
