# admin_app/urls.py
from django.urls import path
from .views import admin_dashboard, farmer_list, customer_list, product_list, order_list

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),  # Admin dashboard view
    path('farmer_list/', farmer_list, name='admin_farmer_list'),  # Farmers list view
    path('customer_list/', customer_list, name='admin_customer_list'),  # Customers list view
    path('product_list/', product_list, name='admin_product_list'),  # Products list view
    path('order_list/', order_list, name='admin_order_list'),  # Orders list view
]
