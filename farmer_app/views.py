from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from product_app.models import Product
from product_app.forms import ProductForm
from django.templatetags.static import static

@login_required
def farmer_dashboard(request):
    products = Product.objects.filter(farmer=request.user, is_deleted=False)  # Get products for the logged-in farmer
    
    # Ensure all products have valid image URLs
    for product in products:
        if not product.image:
            product.image = static('images/default_product.jpg')  # Use static instead of media
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle form submission
        if form.is_valid():
            product = form.save(commit=False)  # Create a product instance without saving to the database yet
            product.farmer = request.user  # Assign the logged-in user as the farmer
            product.save()  # Save the product instance to the database
            return redirect('farmer_dashboard')  # Redirect back to the farmer dashboard
    else:
        form = ProductForm()  # Create a new empty form for adding a product

    context = {
        'products': products,
        'form': form,
        'products_count': products.count(),  # Count of products for the overview
    }

    return render(request, 'farmer_app/farmer_dashboard.html', context)

@login_required
def my_products(request):
    products = Product.objects.filter(farmer=request.user,status='Approved')  # Get the farmer's products
    return render(request, 'farmer_app/my_products.html', {'products': products})
