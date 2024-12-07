from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.templatetags.static import static


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('dairy', 'Dairy'),
        ('tools', 'Tools & Equipment'),
        ('seeds', 'Seeds & Saplings'),
        ('pesticides', 'Pesticides & Fertilizers'),
        ('organic', 'Organic Products'),
        ('livestock', 'Livestock & Feed'),
        ('other', 'Other')
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return static('images/default_product.jpg')

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def is_active(self):
        return not self.is_deleted

    @property
    def status(self):
        return 'Inactive' if self.is_deleted else 'Active'

    @property
    def stock_status(self):
        if self.quantity > 20:
            return "In Stock"
        elif 1 <= self.quantity <= 20:
            return "Low Stock"
        else:
            return "Out of Stock"

    @property
    def stock_status_color(self):
        if self.quantity > 20:
            return "success"  # Green
        elif 1 <= self.quantity <= 20:
            return "warning"  # Orange
        else:
            return "danger"   # Red
