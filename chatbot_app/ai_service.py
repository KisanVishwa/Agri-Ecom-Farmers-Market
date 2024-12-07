import google.generativeai as genai
from django.conf import settings
import logging
from django.core.cache import cache
from .models import APIUsage
import threading

logger = logging.getLogger(__name__)

class ChatbotError(Exception):
    """Base exception for chatbot-related errors"""
    pass

class GeminiServiceError(ChatbotError):
    """Raised when there's an error with Gemini service"""
    pass

class GeminiService:
    _thread_local = threading.local()
    COST_PER_TOKEN = 0.00001  # Update this based on actual Gemini pricing
    
    def __init__(self):
        try:
            if not settings.GEMINI_API_KEY:
                raise GeminiServiceError("Gemini API key not found")
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Gemini initialization error: {str(e)}")
            raise GeminiServiceError(f"Failed to initialize Gemini: {str(e)}")
    
    def _test_connection(self):
        try:
            test_response = self.model.generate_content("Test connection")
            if not test_response:
                raise GeminiServiceError("No response from Gemini API")
        except Exception as e:
            raise GeminiServiceError(f"Connection test failed: {str(e)}")
    
    def _calculate_tokens(self, text):
        # Simple estimation: ~4 chars per token
        return len(text) // 4
    
    def get_response(self, message, user_type, message_type):
        cache_key = f"gemini_response_{user_type}_{hash(f'{message}_{message_type}')}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        try:
            # User-type specific prompts
            base_prompts = {
                'farmer': """You are Kisan Vishwa's AI assistant for farmers. Your role is to:
                    - Provide expert agricultural advice
                    - Share market prices and trends
                    - Guide on crop management and best practices
                    - Help with inventory and selling
                    - Offer weather-related farming advice
                    Always maintain a professional, knowledgeable tone focused on farming.""",
                'customer': """You are Kisan Vishwa's AI assistant for customers. Your role is to:
                    - Help find and select fresh produce
                    - Provide detailed product information
                    - Assist with orders and delivery
                    - Share food storage and usage tips
                    - Guide through the shopping experience
                    Always maintain a friendly, helpful tone focused on shopping."""
            }

            prompt = f"""{base_prompts[user_type]}

            Previous context: The user is a {user_type}.
            Message type: {message_type}
            User query: {message}
            
            Provide a helpful, concise response appropriate for a {user_type}."""
            response = self.model.generate_content(prompt)
            
            # Calculate and log API usage
            input_tokens = self._calculate_tokens(prompt)
            output_tokens = self._calculate_tokens(response.text)
            total_tokens = input_tokens + output_tokens
            cost = total_tokens * self.COST_PER_TOKEN
            
            APIUsage.objects.create(
                endpoint='gemini-pro',
                tokens_used=total_tokens,
                cost=cost,
                user=getattr(self._thread_local, 'current_user', None)
            )
            
            result = {
                'text': response.text,
                'message_type': message_type
            }
            cache.set(cache_key, result, 3600)
            return result
            
        except Exception as e:
            APIUsage.objects.create(
                endpoint='gemini-pro',
                tokens_used=0,
                cost=0,
                success=False,
                error_message=str(e),
                user=getattr(self._thread_local, 'current_user', None)
            )
            return None