from rest_framework import permissions


class IsTaskManager(permissions.BasePermission):
    """Allows access only to task manager."""

    def has_object_permission(self, request, view, obj):

        if request.user.profile == obj.task_manager:
            return True
