from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from api.models import UserProfile

user = get_user_model()


@receiver(post_save, sender=user)
def create_profile(sender, instance, created, **kwargs):
    """Signal handler to create a new UserProfile for each new User
    instance.
    """
    if created:
        UserProfile.objects.create(
            owner=instance
        )


@receiver(post_save, sender=UserProfile)
def save_profile(sender, instance, **kwargs):
    """Signal handler to save the newly created UserProfile instance."""

    instance.save()
