from rest_framework import permissions
from api import models
from django.contrib.auth import get_user_model

User = get_user_model()


class IsTaskManager(permissions.BasePermission):
    """Allows access only to task manager."""

    def has_permission(self, request, view):
        if request and request.user.is_authenticated:

            if request.user.profile.position.is_task_manager:

                return True


class IsOwner(permissions.BasePermission):
    """Allows access only to owner."""

    def has_object_permission(self, request, view, obj):

        # Check if the user is authenticated
        if request and request.user.is_authenticated:

            # Allows access to user-instance owner
            if isinstance(obj, User):
                if request.user == obj:
                    return True

            # Allows access to profile-instance owner
            elif isinstance(obj, models.UserProfile):
                if request.user == obj.owner:
                    return True

            # Allows access to task-group-instance owner
            elif isinstance(obj, models.TaskGroup):
                if request.user.profile == obj.assigned_task.owner:
                    return True

            # Allows access to task-instance owner
            elif isinstance(obj, models.Task):
                if request.user.profile == obj.owner:
                    return True


class IsTeamMember(permissions.BasePermission):
    """Allows access only to task team members."""

    def has_object_permission(self, request, view, obj):

        if request and request.user.is_authenticated:
            if isinstance(obj, models.TaskResource):
                if request.user.profile\
                        in obj.task.task_group.team_members.all():

                    return True
