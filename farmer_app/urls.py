from django.urls import path
from .views import farmer_dashboard, my_products  # Remove add_product as it's not needed

urlpatterns = [
    path('dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('my_products/', my_products, name='my_products'),
]
