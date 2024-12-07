from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductForm
from .models import Product
from customer_app.models import CartItem, Wishlist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
import os
from django.db.models import Q


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            # If no image is uploaded, it will use the default image
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('my_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def my_products(request):
    # Get filter parameters
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'newest')

    # Base queryset
    products = Product.objects.filter(farmer=request.user, is_deleted=False)

    # Apply filters
    if category:
        products = products.filter(category=category)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply sorting
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'oldest':
        products = products.order_by('created_at')
    elif sort_by == 'price-high':
        products = products.order_by('-price')
    elif sort_by == 'price-low':
        products = products.order_by('price')

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    context = {
        'products': products,
        'current_category': category,
        'current_sort': sort_by,
        'search_query': search_query,
        'PRODUCT_CATEGORIES': Product.CATEGORY_CHOICES,
    }
    
    return render(request, 'my_products.html', context)


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Check if clear_image is checked
            if request.POST.get('clear_image'):
                if product.image:
                    try:
                        old_image_path = product.image.path
                        product.image = None
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    except Exception as e:
                        print(f"Error removing image file: {e}")
            
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('my_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'edit_product_page.html', {
        'form': form,
        'product': product
    })


@login_required
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id, farmer=request.user)
            
            # First, delete related cart items
            CartItem.objects.filter(product=product).delete()
            
            # Delete related wishlist items
            Wishlist.objects.filter(product=product).delete()
            
            # Soft delete the product
            product.is_deleted = True
            product.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Product deleted successfully',
                    'remaining_count': Product.objects.filter(farmer=request.user, is_deleted=False).count()
                })
            
            messages.success(request, 'Product deleted successfully!')
            return redirect('my_products')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
            
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('my_products')
    
    return redirect('my_products')


@login_required
def toggle_featured(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, farmer=request.user)
        product.is_featured = not product.is_featured
        product.save()
        messages.success(request, f'Product {"featured" if product.is_featured else "unfeatured"} successfully!')
    return redirect('my_products')


def customer_dashboard(request):
    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:6]
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'customer_app/customer_dashboard.html', context)


@login_required
def clear_product_image(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, farmer=request.user)
        if product.image:
            try:
                old_image_path = product.image.path
                product.image = None
                product.save()
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                messages.success(request, 'Product image cleared successfully!')
            except Exception as e:
                print(f"Error removing image file: {e}")
        
        return redirect('edit_product', product_id=product_id)
    return redirect('edit_product', product_id=product_id)


@login_required
def filter_products(request):
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    products = Product.objects.filter(farmer=request.user)
    
    if category:
        products = products.filter(category=category)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    html = render_to_string('product_grid_partial.html', {
        'products': products,
        'current_category': category
    }, request=request)
    
    return HttpResponse(html)
