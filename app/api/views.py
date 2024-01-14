from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from api import serializers
from api.models import Task, Priority, Status, Category, Position, \
    TaskGroup, UserProfile
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.permissions import IsOwner, IsTaskManager
# Create your views here.

User = get_user_model()


class CustomUserView(ModelViewSet):
    """ModelViewSett for CustomUser model with basic crud functions."""

    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

        if self.action == 'retrieve' or\
                self.action == 'list':
            permission_classes = [IsAuthenticated]

        elif self.action == 'update' or\
                self.action == 'partial_update':
            permission_classes = [IsAdminUser | IsOwner]

        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class PositionView(ModelViewSet):
    """ModelViewSett for Position model with basic crud functions."""

    queryset = Position.objects.all()
    serializer_class = serializers.PositionSerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Allows only admin-users to modify or create instances."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create' or \
                self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class CategoryView(ModelViewSet):
    """ModelViewSett for Category model with basic crud functions."""

    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Allows only admin-users to modify or create instances."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create' or \
                self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class StatusView(ModelViewSet):
    """ModelViewSett for Status model with basic crud functions."""

    queryset = Status.objects.all()
    serializer_class = serializers.StatusSerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Allows only admin-users to modify or create instances."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create' or \
                self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class PriorityView(ModelViewSet):
    """ModelViewSett for Task model with basic crud functions."""

    queryset = Priority.objects.all()
    serializer_class = serializers.PrioritySerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Allows only admin-users to modify or create instances."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create' or \
                self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class UserProfileView(ModelViewSet):
    """ModelViewSett for UserProfile model with basic crud functions."""

    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser]

        elif self.action == 'update' or \
                self.action == 'partial_update':
            permission_classes = [IsAdminUser | IsOwner]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class TaskGroupView(ModelViewSet):
    """ModelViewSett for TaskGroup model with basic crud functions."""

    queryset = TaskGroup.objects.all()
    serializer_class = serializers.TaskGroupSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        # Only admin can manually create/destroy a taskgroup
        elif self.action == 'create' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser]

        elif self.action == 'update' or \
                self.action == 'partial_update':
            permission_classes = [IsAdminUser | IsOwner]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class TaskView(ModelViewSet):
    """ModelViewSett for Task model with basic crud functions."""

    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        # Only admin or authenticated user with a position that has
        # is_task_manager true can create
        elif self.action == 'create':
            permission_classes = [IsAdminUser | IsTaskManager]

        elif self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser | IsOwner]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Assigns the user's profile to the Task as owner."""

        serializer.validated_data['owner'] = self.request.user.profile
        return super().perform_create(serializer)


class LoginView(ObtainAuthToken):
    """Login view for browsable api."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
