from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from api.serializers import TaskSerializer
from api.models import Task
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.permissions import IsTaskManager
# Create your views here.


class TaskView(ModelViewSet):
    """ModelViewSett for Task model with basic crud functions."""

    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action == 'list' or \
                self.action == 'create' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser | IsTaskManager]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Assigns the user's profile to the Task as task_manager."""
        task_manager = self.request.user.profile
        serializer.validated_data['task_manager'] = task_manager
        return super().perform_create(serializer)


class LoginView(ObtainAuthToken):
    """Login view for browsable api."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
