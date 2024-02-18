from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from api import serializers, models, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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

    # Status Change
    @action(detail=True, methods=['PATCH'])
    def change_status(self, request, pk):
        """
        Changes the status of a task and handles all necessary
        modifictions that come with it, like changing dates
        (e.g. Completed_at, due_date). Expects exactly one key value
        pair.

        Expected Key value pair (one of these):
        - 'In Progress' - due_date value (to activate a task after it
            has been archived)
        - 'Completed' - completed_at value (to finish a task)
        - 'Postponed' - due_date value (to mark a task as postponed)
        - 'Archived' - None (to archive a task)
        """

        # Utility function
        def changing_status(status, request_data, task_instance):
            """
            Implements the logic to change the status (e.g. 'In Progress',
            'Completed') and set the provided values (e.g. due_date,
            completed_at) for the task.
            """

            due_date = None
            completed_at = None

            if status == 'In Progress' or \
                    status == 'Postponed' or \
                    status == "Archived":
                due_date = request_data[status]

            elif status == 'Completed':
                completed_at = request_data[status]

            # Setting the required values for the serialization
            request_data['status'] = status
            if due_date:
                request_data['due_date'] = due_date

            elif completed_at:
                request_data['completed_at'] = completed_at

            # Removing the useless key value pair from the
            # request data before serialization
            request_data.pop(status, None)

            serializer = self.get_serializer(
                instance=task_instance,
                data=request_data
            )
            if serializer.is_valid():
                serializer.save()

                return Response(
                    {
                        'message': f'The task got succesfully {status.lower()}'
                    }
                )

            else:
                errors = serializer.errors
                return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        if len(request.data) != 1:
            return Response(
                {
                    'Error': '''Request.data is expected to have only
                    1 key value pair'''
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        expected_statuses = [
            'In Progress', 'Completed', 'Postponed', 'Archived'
        ]
        for status in expected_statuses:
            if status in request.data:

                task_instance = models.Task.objects.get(pk=pk)
                changing_status(status, request.data, task_instance)

            else:
                return Response(
                    {
                        'Error': '''Key provided in the request.data doesnt
                        exist within the system'''
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

    # Statistics for tasks
    @action(detail=False, methods=['GET'])
    def tasks_statistics(self, request):
        """
        Gives numbers of all the tasks acording to their statuses
        within the last 3 months of which the request user is the
        owner. Staff user can see all the tasks in the system 
        independent from ownership status.
        """

        current_date = timezone.now().date()
        three_month_earlier = current_date - timezone.timedelta(days=60)

        # For staff users
        if request.user.is_staff:

            completed_tasks = models.Task.objects.filter(
                status='Completed',
                completed_at__lte=current_date,
                completed_at__gte=three_month_earlier
            ).count()

            postponed_tasks = models.Task.objects.filter(
                status='Postponed',
                completed_at__lte=current_date,
                completed_at__gte=three_month_earlier
            ).count()

            archived_tasks = models.Task.objects.filter(
                status='Archived',
                completed_at__lte=current_date,
                completed_at__gte=three_month_earlier
            ).count()

            tasks_in_progress = models.Task.objects.filter(
                status='In Progress'
            ).count()

        # For non staff users
        else:
            completed_tasks = models.Task.objects.filter(
                owner=request.user,
                status='Completed',
                completed_at__lte=current_date,
                completed_at__gte=three_month_earlier
            ).count()

            postponed_tasks = models.Task.objects.filter(
                owner=request.user,
                status='Postponed',
                completed_at__lte=current_date,
                completed_at__gte=three_month_earlier
            ).count()

            archived_tasks = models.Task.objects.filter(
                owner=request.user,
                status='Archived',
                completed_at__lte=current_date,
                completed_at__gte=three_month_earlier
            ).count()

            tasks_in_progress = models.Task.objects.filter(
                owner=request.user,
                status='In Progress'
            ).count()

        return Response(
            {
                'completed_tasks (last 3 months)': completed_tasks,
                'postponed_tasks (last 3 months)': postponed_tasks,
                'archived_tasks (last 3 months)': archived_tasks,
                'tasks_in_progress (last 3 months)': tasks_in_progress
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
                self.action == 'statistics':
            permission_classes = [IsAdminUser | permissions.IsTaskManager]

        elif self.action == 'update' or \
                self.action == 'partial_update' or \
                self.action == 'destroy' or \
                self.action == 'change_status':
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
