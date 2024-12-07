from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ChatMessage
from django.core.cache import cache
import json
from unittest.mock import patch
from .ai_service import GeminiService, GeminiServiceError

class ChatMessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_chat_message_creation(self):
        """Test ChatMessage model creation and string representation"""
        message = ChatMessage.objects.create(
            user=self.user,
            message="Test message",
            response="Test response",
            message_type='general',
            is_user=True
        )
        self.assertEqual(str(message), f"Chat with {self.user.username} at {message.created_at}")
        
    def test_message_types(self):
        """Test different message types are handled correctly"""
        message_types = ['general', 'product', 'order', 'support', 'weather', 'market']
        for msg_type in message_types:
            message = ChatMessage.objects.create(
                user=self.user,
                message=f"Test {msg_type} message",
                response=f"Test {msg_type} response",
                message_type=msg_type,
                is_user=True
            )
            self.assertEqual(message.message_type, msg_type)

class ChatViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_chat_interface_view(self):
        """Test chat interface is accessible"""
        response = self.client.get(reverse('chatbot_app:chat_interface'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatbot_app/chat.html')
        
    def test_send_message(self):
        """Test message sending functionality"""
        data = {'message': 'Test message'}
        response = self.client.post(
            reverse('chatbot_app:send_message'),
            data,
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatMessage.objects.filter(message='Test message').exists())
        
    def test_empty_message(self):
        """Test empty message handling"""
        data = {'message': ''}
        response = self.client.post(
            reverse('chatbot_app:send_message'),
            data,
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 400)
        
    def test_message_type_detection(self):
        """Test message type detection"""
        test_cases = [
            ('What is the market price?', 'market'),
            ('How is the weather today?', 'weather'),
            ('Track my order', 'order'),
            ('Show available products', 'product'),
            ('I need support', 'support'),
            ('Hello there', 'general'),
        ]
        
        for message, expected_type in test_cases:
            response = self.client.post(
                reverse('chatbot_app:send_message'),
                {'message': message},
                HTTP_HX_REQUEST='true'
            )
            self.assertEqual(response.status_code, 200)
            latest_message = ChatMessage.objects.filter(
                message=message
            ).first()
            self.assertEqual(latest_message.message_type, expected_type)

class ChatMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        cache.clear()
        
    def test_rate_limiting(self):
        """Test rate limiting middleware"""
        # Send 11 messages rapidly
        for i in range(11):
            response = self.client.post(
                reverse('chatbot_app:send_message'),
                {'message': f'Test message {i}'},
                HTTP_HX_REQUEST='true'
            )
            if i < 10:
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 429)
                
    def tearDown(self):
        cache.clear()

class ChatSSETests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_message_stream(self):
        """Test SSE message stream"""
        response = self.client.get(
            reverse('chatbot_app:message_stream'),
            HTTP_ACCEPT='text/event-stream'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

class GeminiServiceTests(TestCase):
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def setUp(self, mock_model, mock_configure):
        # Configure the mock model to avoid actual API calls
        self.mock_model_instance = mock_model.return_value
        self.service = GeminiService()
    
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_successful_response(self, mock_generate):
        # Mock successful response
        mock_generate.return_value.text = "Test response"
        
        response = self.service.get_response(
            message="Test message",
            user_type="farmer",
            message_type="general"
        )
        
        self.assertIsNotNone(response)
        self.assertEqual(response['message_type'], 'general')
    
    def test_farmer_specific_prompt(self):
        response = self.service.get_response(
            message="What are today's tomato prices?",
            user_type="farmer",
            message_type="market"
        )
        self.assertIsNotNone(response)
        self.assertEqual(response['message_type'], 'market')
    
    def test_customer_specific_prompt(self):
        response = self.service.get_response(
            message="How can I track my order?",
            user_type="customer",
            message_type="order"
        )
        self.assertIsNotNone(response)
        self.assertEqual(response['message_type'], 'order')
    
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_api_error_handling(self, mock_generate):
        # Mock API error
        mock_generate.side_effect = Exception("API Error")
        
        response = self.service.get_response(
            message="Test message",
            user_type="farmer",
            message_type="general"
        )
        
        # Should return None to trigger fallback
        self.assertIsNone(response)
