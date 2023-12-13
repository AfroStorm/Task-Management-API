from rest_framework import serializers, permissions
from django.contrib.auth import get_user_model
from .models import UserProfile, Task, Category, Status, Priority, Position, \
    TaskGroup

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


class TaskGroupSerializer(serializers.ModelSerializer):
    """Serializes the TaskGroup model."""

    required_positions = serializers.SlugRelatedField(
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
        fields = ['id', 'name', 'required_positions', 'team_members', 'task']

    def get_fields(self):
        """Prevents the authorized task manager from manually changing the
        task of the TaaskGroup."""
        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        elif request.method not in permissions.SAFE_METHODS:
            fields['task'].read_only = True

            return fields

        return fields


class TaskSerializer(serializers.ModelSerializer):
    """Serializes the Task model."""

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 'category', 'priority',
            'status', 'task_manager', 'task_group'
        ]

    def get_fields(self):
        """Prevents non-admin users from changing the taskgroup for the task.
        """

        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        elif request.method not in permissions.SAFE_METHODS:
            fields['task_group'].read_only = True
            fields['task_manager'].read_only = True

            return fields

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
            return None

        return data
