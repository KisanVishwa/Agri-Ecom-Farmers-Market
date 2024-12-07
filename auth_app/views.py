from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import FarmerProfile, CustomerProfile
from product_app.models import Product

def HomePage(request):
    # Check if user is authenticated but accessing homepage
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'farmerprofile'):
            return redirect('farmer_dashboard')
        elif hasattr(request.user, 'customerprofile'):
            return redirect('customer_dashboard')
    
    # Get featured products for homepage
    featured_products = Product.objects.filter(
        is_featured=True,
        is_deleted=False
    ).order_by('-created_at')[:10]  # Limit to 10 products
    
    return render(request, 'HomePage.html', {
        'featured_products': featured_products
    })


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        role = request.POST.get('role')

        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)

                # Create the correct profile based on role
                if role == 'farmer':
                    FarmerProfile.objects.create(user=user)
                else:
                    CustomerProfile.objects.create(user=user)

                messages.success(request, "Registration successful! You can log in now.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Registration error: {e}")
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Set session expiry to 0 to expire when browser closes
            request.session.set_expiry(0)

            # Check user profile type and redirect accordingly
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'farmerprofile'):
                return redirect('farmer_dashboard')
            elif hasattr(user, 'customerprofile'):
                return redirect('customer_dashboard')
            else:
                messages.error(request, "Profile not found.")
                return redirect('HomePage')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


def logout_view(request):
    try:
        # Clear all session data
        request.session.flush()
        # Logout the user
        logout(request)
        # Redirect to homepage
        response = redirect('HomePage')
        response.delete_cookie('sessionid')
        return response
    except Exception as e:
        # Log the error if needed
        messages.error(request, "Logout failed. Please try again.")
        return redirect('HomePage')

