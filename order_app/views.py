import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404  # Add get_object_or_404
from .models import Order, OrderItem
from customer_app.models import CartItem  # Assuming Cart is in customer_app
from django.contrib.auth.decorators import login_required
from customer_app.models import CartItem
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages

# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        # Fetch cart items for the logged-in user
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items:
            return redirect('customer_app:cart')  # Redirect to cart page if empty

        # Calculate total cart amount
        cart_total = sum(item.total_price for item in cart_items)

        # Convert to paise for Razorpay (1 INR = 100 paise)
        amount_in_paise = int(cart_total * 100)

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create Order and OrderItems
        order = Order.objects.create(
            user=request.user,
            order_id=razorpay_order['id'],
            amount=cart_total
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,  # Assuming `item.product` is a Product object
                quantity=item.quantity,
                price=item.product.price
            )

        context = {
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': razorpay_order['id'],
            'amount': cart_total,  # Pass the original amount in rupees for display
            'amount_in_paise': amount_in_paise,  # Pass paise amount for Razorpay
            'order': order,
        }
        return render(request, 'order_app/payment.html', context)

    return redirect('customer_app:cart')  # Redirect to cart page if empty

@login_required
def payment_callback(request):
    if request.method == 'POST':
        payment_data = request.POST
        razorpay_payment_id = payment_data.get('razorpay_payment_id')
        razorpay_order_id = payment_data.get('razorpay_order_id')

        try:
            # Update order status
            order = Order.objects.get(order_id=razorpay_order_id)
            order.payment_id = razorpay_payment_id
            order.status = 'Paid'
            order.save()

            # Clear the cart
            CartItem.objects.filter(user=request.user).delete()  # Clear CartItems for the user

            # Send confirmation email
            try:
                # Prepare email content
                context = {
                    'user': request.user,
                    'order': order,
                    'order_items': order_items,
                    'total_amount': total_amount,
                }
                
                # Render email content from template
                html_message = render_to_string('order_app/email/order_confirmation.html', context)
                plain_message = render_to_string('order_app/email/order_confirmation.txt', context)
                
                # Send email
                send_mail(
                    subject=f'Order Confirmation - Order #{order.order_id}',
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
            except Exception as e:
                # Log the error but don't stop the order process
                print(f"Failed to send confirmation email: {str(e)}")
            
            return redirect('order_success')
        except Exception as e:
            print(f"Error during payment callback: {e}")
            return redirect('order_failed')  # Redirect to order failure page

    return redirect('customer_app:cart')  # Redirect to home for invalid requests

# order_app/views.py
@login_required
def order_success(request):
    return render(request, 'order_app/order_success.html')

@login_required
def order_failed(request):
    return render(request, 'order_app/order_failed.html')

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Get all possible statuses for the timeline
    order_statuses = [
        ('PENDING', 'Order Placed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered')
    ]
    
    return render(request, 'order_app/track_order.html', {
        'order': order,
        'order_statuses': order_statuses
    })

def test_email(request):
    try:
        send_mail(
            'Test Email',
            'This is a test email from your Django app.',
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )
        messages.success(request, "Test email sent successfully!")
    except Exception as e:
        messages.error(request, f"Failed to send email: {str(e)}")
    return redirect('HomePage')