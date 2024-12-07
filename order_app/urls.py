from django.urls import path
from . import views

urlpatterns = [
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('success/', views.order_success, name='order_success'),
    path('failed/', views.order_failed, name='order_failed'),
    path('track/<str:order_id>/', views.track_order, name='track_order'),
]