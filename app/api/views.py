from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from api import serializers, models, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
# Create your views here.

User = get_user_model()


class CustomUserView(ModelViewSet):
    """
    Modelviewset for CustomUser model with basic crud functions.
    """

    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    authentication_classes = [TokenAuthentication]
    filter_backends = [SearchFilter,]
    search_fields = ['email']

    def get_permissions(self):
        """
        Requires specific permissions depending on the view action and
        the request user.
        """

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
    """
    Modelviewset for Position model with basic crud functions.
    """

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer
    authentication_classes = [TokenAuthentication,]
    filter_backends = [SearchFilter,]
    search_fields = ['title']

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
    """
    Modelviewset for Category model with basic crud functions.
    """

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = [TokenAuthentication,]
    filter_backends = [SearchFilter,]
    search_fields = ['name']

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
    """
    Modelviewset for Status model with basic crud functions.
    """

    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer
    authentication_classes = [TokenAuthentication,]
    filter_backends = [SearchFilter,]
    search_fields = ['caption']

    def get_permissions(self):
        """
        Requires specific permissions depending on the view action and
        the request user.
        """

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
    """
    Modelviewset for Task model with basic crud functions.
    """

    queryset = models.Priority.objects.all()
    serializer_class = serializers.PrioritySerializer
    authentication_classes = [TokenAuthentication,]
    filter_backends = [SearchFilter,]
    search_fields = ['caption']

    def get_permissions(self):
        """
        Requires specific permissions depending on the view action and
        the request user.
        """

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
    """
    Modelviewset for UserProfile model with basic crud functions.
    """

    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    authentication_classes = [TokenAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'owner', 'first_name', 'last_name', 'phone_number', 'position'
    ]
    ordering_fields = [
        'owner', 'first_name', 'last_name', 'position'
    ]

    def get_permissions(self):
        """
        Requires specific permissions depending on the view action and
        the request user.
        """

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
    """
    Modelviewset for TaskGroup model with basic crud functions.
    """

    queryset = models.TaskGroup.objects.all()
    serializer_class = serializers.TaskGroupSerializer
    authentication_classes = [TokenAuthentication]
    filter_backends = [SearchFilter,]
    search_fields = ['name', 'id']

    def get_permissions(self):
        """
        Requires specific permissions depending on the view action and
        the request user.
        """

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
    """
    Modelviewset for Task model with basic crud functions.
    """

    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    authentication_classes = [TokenAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'id', 'owner', 'task_group']
    ordering_fields = [
        'title', 'id', 'due_date', 'category', 'priority',
        'status', 'owner', 'task_group', 'completed_at'
    ]

    # Statistics for tasks
    @action(detail=False, methods=['GET'])
    def tasks_statistics(self, request):
        """
        Gives a list of all the completed tasks and tasks in progress of which
        the request user is the owner. Staff user can see all the tasks in the
        system independent from ownership status.
        """

        current_date = timezone.now()
        three_month_earlier = current_date - timezone.timedelta(days=60)

        total_completed_tasks = models.Task.objects.filter(
            status='Completed',
        ).count()

        if request.user.is_staff:
            total_completed_tasks = models.Task.objects.filter(
                status='Completed'
            ).count()
            total_tasks_in_progress = models.Task.objects.filter(
                status='In Progress'
            ).count()

        else:
            total_completed_tasks = models.Task.objects.filter(
                status='Completed', owner=request.user
            ).count()
            total_tasks_in_progress = models.Task.objects.filter(
                status='In Progress', owner=request.user
            ).count()

        return Response(
            {
                'total_completed_tasks': total_completed_tasks,
                'total_tasks_in_progress': total_tasks_in_progress
            }
        )

    def get_permissions(self):
        """
        Requires specific permissions depending on the view action and
        the request user.
        """

        if self.action == 'list' or \
                self.action == 'retrieve':
            permission_classes = [IsAuthenticated]

        elif self.action == 'create' or \
                self.action == 'tasks_statistics':
            permission_classes = [IsAdminUser | permissions.IsTaskManager]

        elif self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy':
            permission_classes = [
                IsAdminUser | permissions.IsOwner & permissions.IsTaskManager
            ]

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
    search_fields = ['source_name', 'id', 'resource_link', 'task']
    ordering_fields = ['task', 'id', 'resource_link']

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
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
