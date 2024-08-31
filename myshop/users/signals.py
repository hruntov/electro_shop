from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender: type[User], instance: User, created: bool, **kwargs: dict) -> None:
    """
    Signal to create a user profile when a new user is created.

    Args:
        sender (type[User]): The model class that sent the signal.
        instance (User): The instance of the model that was saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs (dict): Additional keyword arguments.

    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender: type[User], instance: User, **kwargs: dict) -> None:
    """
    Signal to save the user profile when the user is saved.

    Args:
        sender (type[User]): The model class that sent the signal.
        instance (User): The instance of the model that was saved.
        **kwargs (dict): Additional keyword arguments.

    """
    instance.profile.save()
