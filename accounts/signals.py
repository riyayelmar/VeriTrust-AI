from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, VerificationProfile



@receiver(post_save, sender=User)
def create_verification_profile(sender, instance, created, **kwargs):

    if created:

        VerificationProfile.objects.create(
            user=instance
        )