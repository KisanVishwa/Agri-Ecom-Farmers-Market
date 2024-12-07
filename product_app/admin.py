from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'farmer', 'is_featured', 'created_at')
    list_filter = ('category', 'created_at', 'farmer', 'is_featured')
    search_fields = ('name', 'description', 'farmer__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    list_editable = ['is_featured']  # Allow quick editing of featured status

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(farmer=request.user)
        return queryset