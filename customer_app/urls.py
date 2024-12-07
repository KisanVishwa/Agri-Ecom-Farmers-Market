from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('cart/', views.customer_cart, name='customer_cart'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('orders/', views.customer_orders, name='customer_orders'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.view_wishlist, name='customer_wishlist'),
    path('update-cart/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('toggle-wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('shop/', views.shop, name='shop'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('addresses/', views.customer_addresses, name='customer_addresses'),
    path('payment-methods/', views.customer_payment_methods, name='customer_payment_methods'),
    path('notifications/', views.customer_notifications, name='customer_notifications'),
    path('support/', views.customer_support, name='customer_support'),
    path('feedback/', views.customer_feedback, name='customer_feedback'),
    path('checkout/', views.checkout, name='checkout'),
]