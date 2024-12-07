from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CartItem, Wishlist
from product_app.models import Product
from django.contrib import messages
from order_app.models import Order
from django.http import JsonResponse
from .forms import AddToCartForm, UpdateCartForm
from django.core.paginator import Paginator
import json
from django.db.models import Q
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import ensure_csrf_cookie
from decimal import Decimal

from order_app.views import initiate_payment

@login_required
def customer_dashboard(request):
    products = Product.objects.filter(is_deleted=False)
    # Cart and Wishlist Counts
    cart_items_count = CartItem.objects.filter(user=request.user).count()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    # Get list of product IDs in user's wishlist
    wishlist_products = Product.objects.filter(wishlist__user=request.user)

    # Add these new queries
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    featured_products = Product.objects.filter(is_deleted=False, is_featured=True)
    total_savings = calculate_total_savings(request.user)  # You'll need to implement this
    orders = Order.objects.filter(user=request.user)

    # Add pagination
    paginator = Paginator(featured_products, 15)  # Show 15 products per page (3 rows × 5 columns)
    page = request.GET.get('page')
    
    try:
        featured_products = paginator.get_page(page)
    except PageNotAnInteger:
        featured_products = paginator.get_page(1)
    except EmptyPage:
        featured_products = paginator.get_page(paginator.num_pages)
    
    context = {
        'products': products,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'wishlist_products': wishlist_products,
        'recent_orders': recent_orders,
        'featured_products': featured_products,
        'total_savings': total_savings,
        'orders': orders
    }
    return render(request, 'customer_app/customer_dashboard.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': 1}
            )
            
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            
            cart_count = CartItem.objects.filter(user=request.user).count()
            
            return JsonResponse({
                'status': 'success',
                'message': f'{product.name} added to cart',
                'cart_count': cart_count
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'customer_app/cart.html', {'cart_items': cart_items})


@login_required
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, 
            product=product
        )
        
        if not created:
            wishlist_item.delete()
            status = 'removed'
        else:
            status = 'added'
            
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': status,
                'wishlist_count': wishlist_count
            })
            
        return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))
    
    return redirect('customer_dashboard')

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'customer_app/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('customer_cart')


@login_required
def view_orders(request):
    # For now, return an empty orders page
    return render(request, 'customer_app/orders.html', {
        'orders': [],  # You can implement order fetching later
    })


# def calculate_total_savings(user):
#     orders = Order.objects.filter(user=user)
#     total_savings = 0
    
#     for order in orders:
#         if hasattr(order.product, 'original_price') and order.product.original_price > order.product.price:
#             savings = (order.product.original_price - order.product.price) * order.quantity
#             total_savings += savings
    
#     return total_savings


@ensure_csrf_cookie
@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        try:
            quantity = int(request.POST.get('quantity', 1))
            if 1 <= quantity <= 99:
                cart_item.quantity = quantity
                cart_item.save()
                
                # Calculate new totals
                cart_items = CartItem.objects.filter(user=request.user)
                cart_total = sum(item.total_price for item in cart_items)
                
                return JsonResponse({
                    'status': 'success',
                    'item_total': float(cart_item.total_price),
                    'cart_total': float(cart_total),
                    'cart_count': cart_items.count()
                })
            
            return JsonResponse({
                'status': 'error',
                'message': 'Quantity must be between 1 and 99'
            }, status=400)
            
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid quantity'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


@login_required
def toggle_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            wishlist_item.delete()
            message = f"{product.name} removed from wishlist"
            status = 'removed'
        else:
            message = f"{product.name} added to wishlist"
            status = 'added'
            
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'status': status,
            'message': message,
            'wishlist_count': wishlist_count
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def shop(request):
    products = Product.objects.filter(is_deleted=False)
    
    # Search filter with Q objects for better search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    categories = dict(Product.CATEGORY_CHOICES)
    
    # Filter by category
    category = request.GET.get('category')
    if category and category != 'all':
        products = products.filter(category=category)
    
    # Update price range filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    try:
        if min_price and min_price.strip():
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        if max_price and max_price.strip():
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
    except ValueError:
        # Handle invalid price inputs gracefully
        messages.error(request, 'Invalid price range entered')
    
    # Sorting
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 15)  # Show 15 products per page (3 rows × 5 columns)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    # Get wishlist products for the user
    wishlist_products = Product.objects.filter(wishlist__user=request.user)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'current_sort': sort_by,
        'wishlist_products': wishlist_products,
        'min_price': min_price,
        'max_price': max_price
    }
    
    return render(request, 'customer_app/shop.html', context)


@login_required
def search_suggestions(request):
    query = request.GET.get('query', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
    ).values('id', 'name')[:5]  # Limit to 5 suggestions
    
    suggestions_list = list(suggestions)
    
    return JsonResponse({
        'suggestions': suggestions_list
    })


@login_required
def toggle_featured(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, farmer=request.user)
        product.is_featured = not product.is_featured
        product.save()
        messages.success(request, f'Product {"featured" if product.is_featured else "unfeatured"} successfully!')
    return redirect('my_products')


def customer_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    context = {
        'cart_items': cart_items
    }
    return render(request, 'customer_app/cart.html', context)


@login_required
def customer_profile(request):
    context = {
        'user': request.user,
        'cart_items_count': CartItem.objects.filter(user=request.user).count(),
        'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
    }
    return render(request, 'customer_app/profile.html', context)


@login_required
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
        'cart_items_count': CartItem.objects.filter(user=request.user).count(),
        'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
    }
    return render(request, 'customer_app/orders.html', context)

@login_required
def customer_addresses(request):
    return render(request, 'customer_app/addresses.html')

@login_required
def customer_payment_methods(request):
    return render(request, 'customer_app/payment_methods.html')

@login_required
def customer_notifications(request):
    return render(request, 'customer_app/notifications.html')

@login_required
def customer_support(request):
    return render(request, 'customer_app/support.html')

@login_required
def customer_feedback(request):
    return render(request, 'customer_app/feedback.html')


@login_required
def checkout(request):
    # Check if the user has items in their cart
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')  # Redirect back to cart if it's empty

    # Redirect to order_app initiate_payment view for payment processing
    return initiate_payment(request)  # This will call the Razorpay payment flow

def calculate_total_savings(user):
    total_savings = 0
    # Retrieve all orders placed by the user
    orders = Order.objects.filter(user=user)

    for order in orders:
        # Iterate over all items in the order
        for order_item in order.items.all():
            product = order_item.product
            # Check if the product has an original price and if the original price is greater than the current price
            if hasattr(product, 'original_price') and product.original_price and product.original_price > product.price:
                # Calculate savings for this item
                savings = (product.original_price - product.price) * order_item.quantity
                total_savings += savings

    return total_savings