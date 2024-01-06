from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from api.models import UserProfile, Task, TaskGroup, Position

User = get_user_model()


# User - UserProfile creation
def create_or_update_profile(sender, instance, created, **kwargs):
    """Signal handler to create or update a new UserProfile for each User
    instance.
    """

    if created or not hasattr(instance, 'profile'):
        # If the profile doesn't exist, create it
        UserProfile.objects.create(
            owner=instance,
            email=instance.email
        )
    else:
        # If the profile exists, update it
        instance.profile.email = instance.email
        instance.profile.save()


# Task - TaskGroup creation
@receiver(post_save, sender=Task)
def create_task_group(sender, instance, created, **kwargs):
    """Signal handler to create a new TaskGroup instance for each new Task
    instance.
    """

    if created:
        task_group = TaskGroup.objects.create(
            name=f'TaskGroup of {instance.title}'
        )
        instance.task_group = task_group

        # Adds the task owner to the team member field
        task_group.team_members.add(instance.owner)

        # Adds sample positions to the suggested_positions field
        if instance.category:
            positions = Position.objects.filter(
                related_category=instance.category
            ).distinct().order_by('title')[:5]

            task_group.suggested_positions.add(*positions)

        instance.save()
