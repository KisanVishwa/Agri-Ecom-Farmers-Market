from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import FarmerProfile, CustomerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check the role and create the appropriate profile
        if instance.email and hasattr(instance, 'farmerprofile'):
            FarmerProfile.objects.create(user=instance)
        else:
            CustomerProfile.objects.create(user=instance)
