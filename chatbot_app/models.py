from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    """
    Enhanced ChatMessage model with message type and status
    """
    MESSAGE_TYPES = [
        ('general', 'General Query'),
        ('product', 'Product Related'),
        ('order', 'Order Related'),
        ('support', 'Customer Support'),
        ('weather', 'Weather Query'),
        ('market', 'Market Prices'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(help_text="The message sent by the user")
    response = models.TextField(help_text="The response from the chatbot")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(
        upload_to='chat_attachments/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="File attachment for the message"
    )
    image_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL for image content"
    )
    link_preview = models.JSONField(
        null=True,
        blank=True,
        help_text="Preview data for shared links"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat with {self.user.username} at {self.created_at}" 

    def get_message_class(self):
        """Return CSS class based on user type and message sender"""
        user_type = 'farmer' if hasattr(self.user, 'farmerprofile') else 'customer'
        return f"kv-{user_type}-{'user' if self.is_user else 'bot'}-message"

class APIUsage(models.Model):
    """Track API usage and costs"""
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=100)
    tokens_used = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=6)
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"API call at {self.timestamp} - Cost: ${self.cost}" 