from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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

    # If a task was not created and a profile already exists update it
    # And if a task was created and profile got already created and assigned
    else:
        instance.profile.email = instance.email
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
