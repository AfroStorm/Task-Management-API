from rest_framework import serializers
from django.contrib.auth import get_user_model
from api import models
from rest_framework.exceptions import ValidationError
from django.db.models.query import QuerySet


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializes the CustomUser model."""

    class Meta:
        model = User
        fields = [
            'email', 'id', 'profile', 'password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_style': 'password'}
            },
            'profile': {'required': False}
        }

    def get_fields(self):
        """Prevents non-staff users from manually changing certain fields
        (profile)."""

        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        else:
            fields['profile'].read_only = True

            return fields


class PrioritySerializer(serializers.ModelSerializer):
    """Serializes the Priority model."""

    class Meta:
        model = models.Priority
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    """Serializes the Status model."""

    class Meta:
        model = models.Status
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Serializes the Category model."""

    class Meta:
        model = models.Category
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    """Serializes the Position model."""
    related_category = serializers.SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = models.Position
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes the UserProfile model."""

    owner = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='email',
        required=False
    )

    class Meta:
        model = models.UserProfile
        fields = [
            'id', 'owner', 'first_name', 'last_name', 'phone_number', 'email',
            'position', 'task_group', 'tasks_to_manage'
        ]
        extra_kwargs = {
            'task_group': {'required': False},
            'tasks_to_manage': {'required': False},
        }

    def get_fields(self):
        """Prevents non staff users from modifying certain fields."""

        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        else:
            read_only_fields = ['owner', 'task_group', 'tasks_to_manage']
            for field in read_only_fields:
                fields[field].read_only = True

        return fields


class TaskGroupSerializer(serializers.ModelSerializer):
    """Serializes the TaskGroup model."""

    suggested_positions = serializers.SlugRelatedField(
        queryset=models.Position.objects.all(),
        many=True,
        slug_field='title'
    )
    team_members = serializers.SlugRelatedField(
        queryset=models.UserProfile.objects.all(),
        many=True,
        slug_field='email'
    )

    class Meta:
        model = models.TaskGroup
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
        queryset=models.UserProfile.objects.all(),
        slug_field='email',
        required=False
    )
    category = serializers.SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )
    priority = serializers.SlugRelatedField(
        queryset=models.Priority.objects.all(),
        slug_field='caption'
    )
    status = serializers.SlugRelatedField(
        queryset=models.Status.objects.all(),
        slug_field='caption'
    )
    task_resource = serializers.SlugRelatedField(
        queryset=models.TaskResource.objects.all(),
        many=True,
        slug_field='title',
        required=False
    )

    class Meta:
        model = models.Task
        fields = [
            'id', 'title', 'description', 'due_date', 'category', 'priority',
            'status', 'owner', 'task_group', 'task_resource'
        ]
        extra_kwargs = {
            'task_group': {'required': False}
        }

    def get_fields(self):
        """Sets certain fields to read_only for non staff users."""

        request = self.context.get('request')
        fields = super().get_fields()

        # Staff users have no restrictions
        if hasattr(request, 'user'):
            if request.user.is_staff:
                return fields

            else:
                fields['task_group'].read_only = True
                fields['owner'].read_only = True

                return fields

        return {}

    def to_representation(self, instance):
        """Restricts users from seeing tasks in which they are not a team
        member, except for staff users.."""

        request = self.context.get('request')
        data = super().to_representation(instance)

        if request.user.is_staff:
            return data

        elif hasattr(instance.task_group, 'team_members'):
            if request.user.profile in \
                    instance.task_group.team_members.all():

                return data

            else:
                return {}

        # For newly created instances
        return data


class TaskResourceSerializer(serializers.ModelSerializer):
    """Serializes the TaskResource model."""

    class Meta:
        model = models.TaskResource
        fields = [
            'id', 'source_name', 'description', 'resource_link', 'task'
        ]

    def validate(self, data):
        """Validate that the user is a team member of the selected task."""

        request = self.context['request']

        if request.user.is_staff:
            return data

        # Check if its updated or created, in case of a partial update that
        # excludes a new task instance from the submitted data, no
        # team member check is required.
        if 'task' in data:
            task_instance = data['task']
            # Check if the user is a team member of the selected task
            if request.user.profile not in\
                    task_instance.task_group.team_members.all():

                raise ValidationError(
                    '''The request user is not a member of the selected task's
                    team.'''
                )

        return data

    def to_representation(self, instance):
        """Restricts users from seeing task resources of tasks in which
        they are not a team member, except for staff users.."""

        request = self.context['request']
        data = super().to_representation(instance)

        if request.user.is_staff or request.user.profile\
                in instance.task.task_group.team_members.all():

            return data

        else:
            return {}
