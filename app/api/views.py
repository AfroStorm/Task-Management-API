from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from api.serializers import TaskSerializer, PrioritySerializer, \
    StatusSerializer, CategorySerializer, PositionSerializer, \
    TaskGroupSerializer, UserProfileSerializer
from api.models import Task, Priority, Status, Category, Position, \
    TaskGroup, UserProfile
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.permissions import IsOwner, IsTaskManager
# Create your views here.


class PositionView(ModelViewSet):
    """ModelViewSett for Position model with basic crud functions."""

    queryset = Position.objects.all()
    serializer_class = PositionSerializer
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
    serializer_class = CategorySerializer
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
    serializer_class = StatusSerializer
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
    serializer_class = PrioritySerializer
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
    serializer_class = UserProfileSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Safe methods allowed to authenticated users. Update and partial
        update allowed to owner. Admin has all rights."""

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
    serializer_class = TaskGroupSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Gives specific permissions depending on the view actions."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        # Only admin can manually create/destroy a taskgroup
        elif self.action == 'create' and \
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
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Gives specific permissions depending on the view actions."""

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
        owner = self.request.user.profile
        serializer.validated_data['owner'] = owner
        return super().perform_create(serializer)


class LoginView(ObtainAuthToken):
    """Login view for browsable api."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
