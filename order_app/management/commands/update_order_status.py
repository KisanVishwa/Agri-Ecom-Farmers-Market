from django.core.management.base import BaseCommand
from order_app.models import Order
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates order statuses automatically'

    def handle(self, *args, **kwargs):
        # Get current time
        current_time = timezone.now()
        
        # Get all pending orders older than 1 hour
        pending_orders = Order.objects.filter(
            status='PENDING',
            created_at__lte=current_time - timedelta(hours=1)
        )
        
        for order in pending_orders:
            order.status = 'PROCESSING'
            order.save()
            self._send_status_update_email(order)

        # Get processing orders older than 24 hours
        processing_orders = Order.objects.filter(
            status='PROCESSING',
            created_at__lte=current_time - timedelta(days=1)
        )
        
        for order in processing_orders:
            order.status = 'SHIPPED'
            order.estimated_delivery = (current_time + timedelta(days=3)).date()
            order.save()
            self._send_status_update_email(order)

        self.stdout.write(self.style.SUCCESS('Successfully updated order statuses'))

    def _send_status_update_email(self, order):
        subject = f'Order Status Update - {order.order_id}'
        message = f'''
        Dear {order.user.first_name or order.user.username},
        
        Your order {order.order_id} has been updated to: {order.get_status_display()}
        
        {f"Estimated delivery date: {order.estimated_delivery}" if order.estimated_delivery else ""}
        
        Track your order here: http://yourdomain.com/order/track/{order.order_id}/
        
        Thank you for shopping with Kisan Vishwa!
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email],
                fail_silently=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Sent email for order {order.order_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email for order {order.order_id}: {str(e)}')) 