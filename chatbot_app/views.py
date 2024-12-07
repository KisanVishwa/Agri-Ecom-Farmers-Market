from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from .models import ChatMessage
from .ai_service import GeminiService
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)
gemini_service = GeminiService()

@login_required
def get_messages(request):
    """Retrieve chat messages for the current user only"""
    messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
    user_type = 'farmer' if hasattr(request.user, 'farmerprofile') else 'customer'
    return render(request, 'chatbot_app/messages.html', {
        'messages': messages,
        'user_type': user_type
    })

@require_http_methods(["POST"])
def send_message(request):
    if not request.user.is_authenticated:
        return HttpResponse(
            '<div class="message bot-message">'
            f'<p>Please <a href="{reverse("login")}?next={request.path}">log in</a> to start chatting</p>'
            '</div>',
            status=401
        )
    
    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'}, status=400)
        
    try:
        message_type = determine_message_type(message)
        user_type = 'farmer' if hasattr(request.user, 'farmerprofile') else 'customer'
        
        # Save user message
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            is_user=True,
            message_type=message_type
        )
        
        # Get AI response with user type
        ai_response = gemini_service.get_response(message, user_type, message_type)
        if ai_response is None:
            ai_response = get_bot_response(message, user_type, message_type)
        
        # Save bot response
        ChatMessage.objects.create(
            user=request.user,
            message=ai_response['text'],
            is_user=False,
            message_type=message_type
        )
        
        # Return all messages in chronological order
        messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
        return render(request, 'chatbot_app/messages.html', {'messages': messages})
        
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def toggle_chat(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    
    is_visible = request.session.get('chat_visible', False)
    request.session['chat_visible'] = not is_visible
    
    if not is_visible:  # Opening the chat
        messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
        user_type = 'farmer' if hasattr(request.user, 'farmerprofile') else 'customer'
        
        if not messages:
            welcome_message = (
                "Hello farmer! How can I help you with your farming business today?" 
                if user_type == 'farmer' 
                else "Welcome! How can I assist you with your shopping today?"
            )
            ChatMessage.objects.create(
                user=request.user,
                message=welcome_message,
                is_user=False,
                message_type='general'
            )
            messages = ChatMessage.objects.filter(user=request.user)
        
        return TemplateResponse(request, 'chatbot_app/chat_widget.html', {
            'messages': messages,
            'show_chat_content': True,
            'user_type': user_type
        })
    
    return HttpResponse('')

def determine_message_type(message):
    message = message.lower()
    if any(word in message for word in ['price', 'cost', 'rate', 'market']): return 'market'
    elif any(word in message for word in ['weather', 'rain', 'temperature']): return 'weather'
    elif any(word in message for word in ['order', 'delivery', 'track']): return 'order'
    elif any(word in message for word in ['product', 'stock', 'available']): return 'product'
    elif any(word in message for word in ['help', 'support', 'contact']): return 'support'
    return 'general'

def get_bot_response(message, user_type, message_type):
    from .responses import get_farmer_response, get_customer_response
    if user_type == 'farmer':
        return get_farmer_response(message, message_type)
    return get_customer_response(message, message_type)