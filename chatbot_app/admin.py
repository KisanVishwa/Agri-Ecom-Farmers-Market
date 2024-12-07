from django.contrib import admin
from .models import ChatMessage, APIUsage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_type', 'is_user', 'created_at')
    list_filter = ('message_type', 'is_user', 'created_at')
    search_fields = ('user__username', 'message', 'response')
    readonly_fields = ('created_at',)

@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'endpoint', 'tokens_used', 'cost', 'success', 'user')
    list_filter = ('endpoint', 'success', 'timestamp')
    search_fields = ('user__username', 'error_message')
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
