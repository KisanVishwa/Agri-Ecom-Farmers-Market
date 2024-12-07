from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),                   # Default Admin panel
    path('', include('auth_app.urls')),                # Auth-related URLs
    path('custom-admin/', include('admin_app.urls')),   # Custom admin dashboard URLs
    path('farmer/', include('farmer_app.urls')),        # Farmer-related URLs
    path('products/', include('product_app.urls')),     # Product-related URLs
    path('customer/', include('customer_app.urls')),    # Customer-related URLs
    path('product_app/', include('product_app.urls')),  # Add this line
    path('chatbot/', include('chatbot_app.urls', namespace='chatbot_app')),
    path('order/', include('order_app.urls',)),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add media URL patterns
if settings.DEBUG:  # Serve media files only in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
