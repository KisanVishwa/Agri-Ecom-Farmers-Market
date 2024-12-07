from .models import Wishlist, CartItem
from product_app.models import Product

def wishlist_and_cart_counts(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        wishlist_items = Wishlist.objects.filter(user=request.user)
        
        return {
            'cart_items_count': cart_items.count(),
            'cart_total': sum(item.total_price for item in cart_items),
            'wishlist_count': wishlist_items.count(),
            'wishlist_product_ids': set(item.product_id for item in wishlist_items)
        }
    return {
        'cart_items_count': 0,
        'cart_total': 0,
        'wishlist_count': 0,
        'wishlist_product_ids': set()
    }

def wishlist_status(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        return {
            'wishlist_product_ids': set(item.product.id for item in wishlist_items),
            'wishlist_products': [item.product for item in wishlist_items]
        }
    return {
        'wishlist_product_ids': set(),
        'wishlist_products': []
    }

def product_categories(request):
    """
    Provides product categories and their icons for consistent use across templates
    """
    CATEGORY_ICONS = {
        'vegetables': 'fa-carrot',
        'fruits': 'fa-apple-alt',
        'grains': 'fa-wheat',
        'dairy': 'fa-cheese',
        'tools': 'fa-tools',
        'seeds': 'fa-seedling',
        'pesticides': 'fa-spray-can',
        'organic': 'fa-leaf',
        'livestock': 'fa-cow',
        'other': 'fa-box'
    }
    
    return {
        'PRODUCT_CATEGORIES': Product.CATEGORY_CHOICES,
        'CATEGORY_ICONS': CATEGORY_ICONS
    } 