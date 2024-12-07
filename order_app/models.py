from django.db import models
from django.contrib.auth.models import User
from product_app.models import Product  # Import the Product model

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Order Placed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=100, unique=True, primary_key=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    shipping_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"  # Assuming Product model has a 'name' field