from rest_framework import permissions


class IsTaskManager(permissions.BasePermission):
    """Allows access only to task manager."""

    def has_object_permission(self, request, view, obj):

        if request.user.profile == obj.task_manager and \
                request.user.is_authenticated:
            return True


class IsOwner(permissions.BasePermission):
    """Allows access only to owner."""

    def has_object_permission(self, request, view, obj):

        if request.method not in permissions.SAFE_METHODS:
            if request.user == obj.owner and \
                    request.user.is_authenticated:
                return True
