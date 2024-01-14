from rest_framework import permissions
from api.models import UserProfile, Task, TaskGroup
from django.contrib.auth import get_user_model

User = get_user_model()


class IsTaskManager(permissions.BasePermission):
    """Allows access only to task manager."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.profile.position.is_task_manager:

                return True


class IsOwner(permissions.BasePermission):
    """Allows access only to owner."""

    def has_object_permission(self, request, view, obj):

        # Check if the user is authenticated
        if request.user.is_authenticated:

            # Allows access to user owner
            if isinstance(obj, User):
                if request.user == obj:
                    return True

            # Allows access to profile owner
            elif isinstance(obj, UserProfile):
                if request.user == obj.owner:
                    return True

            # Allows access to task owner
            elif isinstance(obj, TaskGroup):
                if request.user.profile == obj.assigned_task.owner:
                    return True

            # Allows access to task owner
            elif isinstance(obj, Task):
                if request.user.profile == obj.owner:
                    return True

        # For unauthenticated users, deny access
        return False
