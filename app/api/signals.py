from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.models import UserProfile, Task, TaskGroup, Position

User = get_user_model()


# User - UserProfile creation
@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """Signal handler to create or update a new UserProfile for each User
    instance.
    """

    # If a task was created and no profile already exists
    if created and not hasattr(instance, 'profile'):
        profile = UserProfile.objects.create(
            owner=instance,
            email=instance.email
        )
        profile.save()

    # In any other case must always synchronize the profile owner/email
    # (profile.email=instance.email, profile.owner=instance)
    elif created and hasattr(instance, 'profile'):
        instance.profile.email = instance.email
        instance.profile.owner = instance
        instance.profile.save()


# Task - TaskGroup creation
@receiver(post_save, sender=Task)
def create_task_group(sender, instance, created, **kwargs):
    """Signal handler to create a new TaskGroup instance for each new Task
    instance.
    """

    if created and not instance.task_group:
        task_group = TaskGroup.objects.create(
            name=f'TaskGroup of {instance.title}'
        )
        instance.task_group = task_group

        # Adds the task owner to the team member field
        task_group.team_members.add(instance.owner)

        # Adds sample positions to the suggested_positions field
        if instance.category:
            positions = Position.objects.filter(
                category=instance.category
            ).distinct().order_by('id')[:4]

            task_group.suggested_positions.add(*positions)

        instance.save()


# Task - created_at field
@receiver(post_save, sender=Task)
def set_task_completion_date(sender, instance, created, **kwargs):
    """
    Checks if the status of the task is completed and sets the completed_at
    field of the task to the current date.
    """

    if not instance.completed_at and instance.status == 'Completed':
        instance.completed_at = timezone.now()
        instance.save()
