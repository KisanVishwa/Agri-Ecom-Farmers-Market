from django.urls import path
from .views import HomePage, register, login_view, logout_view

urlpatterns = [
    path('', HomePage, name='HomePage'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
