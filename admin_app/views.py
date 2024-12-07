from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from auth_app.models import FarmerProfile, CustomerProfile
from product_app.models import Product
from customer_app.models import CartItem  # Use CartItem instead of an Order model
from order_app.models import Order  # Import Order model
from django.contrib import messages

# Custom check to ensure only superusers can access the admin dashboard
def admin_check(user):
    return user.is_superuser

# Ensure the user is logged in and passes the admin check
@login_required
@user_passes_test(admin_check)
def admin_dashboard(request):
    # Count the number of farmers, customers, products, and orders
    farmer_count = FarmerProfile.objects.count()
    customer_count = CustomerProfile.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()  # Add this line

    context = {
        'farmer_count': farmer_count,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,  # Add this to context
    }

    # Render the admin dashboard template
    return render(request, 'admin_app/admin_dashboard.html', context)


# View to list all farmers
@login_required
@user_passes_test(admin_check)
def farmer_list(request):
    farmers = FarmerProfile.objects.all()
    context = {
        'farmers': farmers,
    }
    return render(request, 'admin_app/farmer_list.html', context)


# View to list all customers
@login_required
@user_passes_test(admin_check)
def customer_list(request):
    customers = CustomerProfile.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'admin_app/customer_list.html', context)


# View to list all products
@login_required
@user_passes_test(admin_check)
def product_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'remove_product':
            product_id = request.POST.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
                product.delete()  # Or product.soft_delete() if you have soft delete
                messages.success(request, f'Product "{product.name}" has been removed successfully.')
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
            return redirect('admin_product_list')

    # Get all farmers with their products
    farmers = FarmerProfile.objects.all()
    farmer_products = {}
    
    for farmer in farmers:
        products = Product.objects.filter(farmer=farmer.user)
        if products.exists():
            farmer_products[farmer] = products

    context = {
        'farmer_products': farmer_products,
        'total_products': Product.objects.count(),
    }
    return render(request, 'admin_app/product_list.html', context)


# View to list all cart items (as a substitute for order list)
@login_required
@user_passes_test(admin_check)
def order_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'remove_order':
            order_id = request.POST.get('order_id')
            try:
                order = Order.objects.get(order_id=order_id)
                order.delete()
                messages.success(request, f'Order #{order_id} has been removed successfully.')
            except Order.DoesNotExist:
                messages.error(request, 'Order not found.')
            return redirect('admin_order_list')

    # Get all customers with their orders
    customers = CustomerProfile.objects.all()
    customer_orders = {}
    
    for customer in customers:
        orders = Order.objects.filter(user=customer.user).order_by('-created_at')
        if orders.exists():  # Only add customers who have orders
            customer_orders[customer] = orders

    context = {
        'customer_orders': customer_orders,
        'total_orders': Order.objects.count(),
    }
    return render(request, 'admin_app/order_list.html', context)

def get_farmer_response(message):
    """
    Enhanced response system for farmer queries
    """
    message = message.lower()
    
    # Product Management Responses
    if any(word in message for word in ['add product', 'sell', 'list']):
        return {
            'text': "To add a new product:\n1. Go to 'My Products'\n2. Click 'Add New Product'\n3. Fill in details\n4. Upload photos\n5. Set price and stock",
            'links': ['/farmer/products/add/'],
            'type': 'product_management'
        }
    
    # Pricing Queries
    elif any(word in message for word in ['price', 'pricing', 'cost']):
        return {
            'text': "Current market trends suggest:\n- Organic products: 20-30% premium\n- Seasonal items: Check local market rates\n- Bulk discounts: Consider for large orders",
            'links': ['/market-trends/'],
            'type': 'pricing'
        }
    
    # Weather Related
    elif any(word in message for word in ['weather', 'rain', 'forecast']):
        return {
            'text': "I can help you check weather forecasts for better crop planning. Please specify your location.",
            'type': 'weather'
        }
    
    # Stock Management
    elif any(word in message for word in ['stock', 'inventory', 'quantity']):
        return {
            'text': "Manage your stock effectively:\n1. Regular updates\n2. Set low stock alerts\n3. Track seasonal demands",
            'links': ['/farmer/inventory/'],
            'type': 'inventory'
        }

def get_customer_response(message):
    """
    Enhanced response system for customer queries
    """
    message = message.lower()
    
    # Product Search
    if any(word in message for word in ['find', 'search', 'looking for']):
        return {
            'text': "I can help you find products! What type are you looking for:\n1. Vegetables\n2. Fruits\n3. Grains\n4. Organic products",
            'links': ['/products/search/'],
            'type': 'search'
        }
    
    # Order Status
    elif any(word in message for word in ['order', 'delivery', 'track']):
        return {
            'text': "You can:\n1. Track your order in 'My Orders'\n2. Check delivery status\n3. Contact the seller",
            'links': ['/customer/orders/'],
            'type': 'order'
        }
    
    # Product Quality
    elif any(word in message for word in ['quality', 'fresh', 'organic']):
        return {
            'text': "Our quality assurance:\n1. Direct from farmers\n2. Freshness guaranteed\n3. Quality checks\n4. Easy returns",
            'type': 'quality'
        }
    
    # Seasonal Products
    elif any(word in message for word in ['season', 'available', 'when']):
        return {
            'text': "I can help you find seasonal products and their availability. What are you interested in?",
            'links': ['/seasonal-products/'],
            'type': 'seasonal'
        }
