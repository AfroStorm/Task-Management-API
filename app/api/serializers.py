from rest_framework import serializers, permissions
from django.contrib.auth import get_user_model
from .models import UserProfile, Task, Category, Status, Priority, Position, \
    TaskGroup
from django.db.models.query import QuerySet


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializes the CustomUser model."""

    class Meta:
        model = User
        fields = [
            'email', 'id'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_style': 'password'}
            }
        }

    def get_fields(self):
        """Prevents non-staff users from manually changing certain fields
        (profile)."""

        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        elif request.methods not in permissions.SAFE_METHODS:
            fields['profile'].read_only = True

            return fields

        return fields


class PrioritySerializer(serializers.ModelSerializer):
    """Serializes the Priority model."""

    class Meta:
        model = Priority
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    """Serializes the Status model."""

    class Meta:
        model = Status
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Serializes the Category model."""

    class Meta:
        model = Category
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    """Serializes the Position model."""

    class Meta:
        model = Position
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes the UserProfile model."""

    class Meta:
        model = UserProfile
        fields = [
            'id', 'owner', 'first_name', 'last_name', 'phone_number', 'email',
            'position', 'task_groups', 'tasks_to_manage'
        ]

    def get_fields(self):
        """Prevents unauthorized users from modifying certain fields."""

        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        elif request.user.is_authenticated:
            read_only_fields = ['owner', 'task_groups', 'tasks_to_manage']
            for field in read_only_fields:
                fields[field].read_only = True

        # Unatuhenticated users all fields will be read only
        else:
            for field in fields:
                fields[field].read_only = True

        return fields


class TaskGroupSerializer(serializers.ModelSerializer):
    """Serializes the TaskGroup model."""

    suggested_positions = serializers.SlugRelatedField(
        queryset=Position.objects.all(),
        many=True,
        slug_field='title'
    )
    team_members = serializers.SlugRelatedField(
        queryset=UserProfile.objects.all(),
        many=True,
        slug_field='email'
    )

    class Meta:
        model = TaskGroup
        fields = ['id', 'name', 'suggested_positions',
                  'team_members', 'assigned_task']

    def get_fields(self):
        """Prevents non-staff users and non-owners from modifying certain fields."""

        request = self.context.get('request')
        fields = super().get_fields()

        if request and request.user.is_staff:
            return fields

        # Checks if self.instance is a query set
        elif isinstance(self.instance, QuerySet):
            # Checks if the request user profile is the owner of the assigned task of the task group
            for obj in self.instance:
                if hasattr(obj.assigned_task, 'owner') and \
                        request.user.profile == obj.assigned_task.owner:
                    fields['assigned_task'].read_only = True

                    return fields

        # Checks if its a single instance
        elif hasattr(self.instance.assigned_task, 'owner') and \
                request.user.profile == self.instance.assigned_task.owner:
            fields['assigned_task'].read_only = True

            return fields

        return {}

    def to_representation(self, instance):
        """Prevents non-staff users from viewing tasks in which they are not
        included."""

        request = self.context['request']
        data = super().to_representation(instance)

        if request.user.is_staff:
            return data

        # If the UserProfile is not a member of the task group.
        elif request.user.profile not in \
                instance.team_members.all():

            return {}

        return data


class TaskSerializer(serializers.ModelSerializer):
    """Serializes the Task model."""
    owner = serializers.SlugRelatedField(
        queryset=UserProfile.objects.all(),
        slug_field='email',
        required=False
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    priority = serializers.SlugRelatedField(
        queryset=Priority.objects.all(),
        slug_field='caption'
    )
    status = serializers.SlugRelatedField(
        queryset=Status.objects.all(),
        slug_field='caption'
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 'category', 'priority',
            'status', 'owner', 'task_group'
        ]
        extra_kwargs = {
            'task_group': {'required': False}
        }

    def get_fields(self):
        """Prevents unauthorized users from modifying certain fields."""
        request = self.context['request']
        fields = super().get_fields()
        # Debugging line
        print(f"Type of self.instance: {type(self.instance)}")

        if request.user.is_staff:
            return fields

        # Check if self.instance is a queryset
        elif isinstance(self.instance, QuerySet):
            for obj in self.instance:
                if hasattr(obj, 'owner') and \
                        request.user.profile == obj.owner:
                    fields['task_group'].read_only = True
                    fields['owner'].read_only = True
                    break

        # Check if self.instance is a single instance
        elif hasattr(self.instance, 'owner') and \
                request.user.profile == self.instance.owner:
            fields['task_group'].read_only = True
            fields['owner'].read_only = True

        return fields

    def to_representation(self, instance):
        """Prevents non-staff users from viewing tasks in which they are not
        included."""

        request = self.context['request']
        data = super().to_representation(instance)

        if request.user.is_staff:
            return data

        # If the UserProfile is not a member of the Task's TaskGroup.
        elif request.user.profile not in \
                instance.task_group.team_members.all():

            return {}

        return data
