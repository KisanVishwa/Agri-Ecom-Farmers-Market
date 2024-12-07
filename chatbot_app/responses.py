def get_farmer_response(message, message_type):
    """
    Generate farmer-specific responses based on message type
    """
    responses = {
        'market': {
            'text': "Here's the current market information:\n"
                   "1. Check current prices\n"
                   "2. View price trends\n"
                   "3. Compare with nearby markets",
            'links': ['/market-prices/', '/price-trends/']
        },
        'weather': {
            'text': "Would you like to:\n"
                   "1. Check today's weather\n"
                   "2. View weekly forecast\n"
                   "3. Get crop-specific weather alerts",
            'links': ['/weather-forecast/']
        },
        'product': {
            'text': "Manage your products:\n"
                   "1. Add new products\n"
                   "2. Update inventory\n"
                   "3. View product performance",
            'links': ['/farmer/products/']
        }
    }
    
    return responses.get(message_type, {
        'text': "How can I help you with your farming business today?",
        'links': ['/farmer/dashboard/']
    }) 

def get_customer_response(message, message_type):
    """
    Generate customer-specific responses based on message type
    """
    responses = {
        'product': {
            'text': "I can help you with products:\n"
                   "1. Browse available products\n"
                   "2. Check product details\n"
                   "3. View product reviews",
            'links': ['/products/', '/categories/']
        },
        'order': {
            'text': "Order assistance:\n"
                   "1. Track your order\n"
                   "2. View order history\n"
                   "3. Return/refund help",
            'links': ['/orders/', '/returns/']
        },
        'support': {
            'text': "Customer support options:\n"
                   "1. Contact seller\n"
                   "2. Report an issue\n"
                   "3. FAQs",
            'links': ['/support/', '/contact/']
        }
    }
    
    return responses.get(message_type, {
        'text': "How can I assist you with your shopping today?",
        'links': ['/shop/']
    }) 