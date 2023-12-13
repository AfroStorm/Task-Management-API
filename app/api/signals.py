from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from api.models import UserProfile, Task, TaskGroup

User = get_user_model()


# User - UserProfile creation
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Signal handler to create a new UserProfile for each new User
    instance.
    """

    if created:
        UserProfile.objects.create(
            owner=instance,
            email=instance.email
        )
        instance.profile.save()


# Task - TaskGroup creation
@receiver(post_save, sender=Task)
def creaate_task_group(sender, instance, created, **kwargs):
    """Signal handler to create a new TaskGroup instance for each new Task
    instance.
    """

    if created:
        task_group = TaskGroup.objects.create(
            name=f'TaskGroup of {instance.title}'
        )
        instance.task_group = task_group
        instance.save()

        if instance.task_manager:
            task_group.team_members.add(instance.task_manager)
