from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from api import serializers, models, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# Create your views here.

User = get_user_model()


class CustomUserView(ModelViewSet):
    """Modelviewset for CustomUser model with basic crud functions."""

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
            permission_classes = [IsAdminUser | permissions.IsOwner]

        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class PositionView(ModelViewSet):
    """Modelviewset for Position model with basic crud functions."""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

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
    """Modelviewset for Category model with basic crud functions."""

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

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
    """Modelviewset for Status model with basic crud functions."""

    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

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
    """Modelviewset for Task model with basic crud functions."""

    queryset = models.Priority.objects.all()
    serializer_class = serializers.PrioritySerializer
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

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
    """Modelviewset for UserProfile model with basic crud functions."""

    queryset = models.UserProfile.objects.all()
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
            permission_classes = [IsAdminUser | permissions.IsOwner]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class TaskGroupView(ModelViewSet):
    """Modelviewset for TaskGroup model with basic crud functions."""

    queryset = models.TaskGroup.objects.all()
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
            permission_classes = [IsAdminUser | permissions.IsOwner]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class TaskView(ModelViewSet):
    """Modelviewset for Task model with basic crud functions."""

    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """Requires specific permissions depending on the view action and
        the request user."""

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create':
            permission_classes = [IsAdminUser | permissions.IsTaskManager]

        elif self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [IsAdminUser | permissions.IsOwner]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Assigns the user's profile to the Task as owner except if staff
        has already submittted an owner."""

        if 'owner' not in serializer.validated_data:
            serializer.validated_data['owner'] = self.request.user.profile
        return super().perform_create(serializer)


class TaskResourceView(ModelViewSet):
    """Modelviewset for TaskResource model with basic crud functions."""

    queryset = models.TaskResource.objects.all()
    serializer_class = serializers.TaskResourceSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action == 'retrieve' or\
                self.action == 'list' or\
                self.action == 'create':
            permission_classes = [IsAuthenticated]

        elif self.action == 'update' or\
                self.action == 'partial_update' or\
                self.action == 'destroy':
            permission_classes = [IsAdminUser | permissions.IsTeamMember]

        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class LoginView(ObtainAuthToken):
    """Login view for browsable api."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
