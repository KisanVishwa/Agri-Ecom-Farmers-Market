from django.core.cache import cache
from django.http import HttpResponse
import time
import logging
from .ai_service import GeminiService

logger = logging.getLogger(__name__)

class ChatRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/chat/send/'):
            user_id = request.user.id
            current_time = time.time()
            
            # Get user's message timestamps from cache
            cache_key = f'chat_rate_limit_{user_id}'
            timestamps = cache.get(cache_key, [])
            
            # Remove timestamps older than 1 minute
            timestamps = [ts for ts in timestamps if current_time - ts < 60]
            
            # Check if user has exceeded rate limit (10 messages per minute)
            if len(timestamps) >= 10:
                return HttpResponse(
                    "Please wait before sending more messages.",
                    status=429  # 429 is the status code for Too Many Requests
                )
            
            # Add current timestamp and update cache
            timestamps.append(current_time)
            cache.set(cache_key, timestamps, 60)

        return self.get_response(request) 

class ChatDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/chatbot/'):
            logger.debug(f'Chat request: {request.path}')
            logger.debug(f'Request method: {request.method}')
            logger.debug(f'HTMX request: {request.headers.get("HX-Request")}')
            logger.debug(f'Session data: {dict(request.session)}')
        
        response = self.get_response(request)
        
        if request.path.startswith('/chatbot/'):
            logger.debug(f'Response status: {response.status_code}')
        
        return response

class APITrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Store user in thread-local storage
            setattr(GeminiService._thread_local, 'current_user', request.user)
        
        try:
            response = self.get_response(request)
            return response
        finally:
            # Always clean up thread-local storage
            if hasattr(GeminiService._thread_local, 'current_user'):
                delattr(GeminiService._thread_local, 'current_user')