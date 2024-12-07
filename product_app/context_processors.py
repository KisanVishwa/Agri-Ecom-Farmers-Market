from .models import Product

def product_categories(request):
    return {
        'PRODUCT_CATEGORIES': Product.CATEGORY_CHOICES,
        'CATEGORY_ICONS': {
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
    } 