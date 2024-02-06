from rest_framework import serializers
from django.contrib.auth import get_user_model
from api import models
from rest_framework.exceptions import ValidationError
from django.db.models.query import QuerySet

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    This serializer is designed to handle the User model with custom behavior
    such as read-only profile for non-staff users and password input styling.

    Attributes:
        password: A write-only field with password input styling.
        profile: An optional field for user profile information.
    """

    class Meta:
        model = User
        fields = ['email', 'id', 'profile', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_style': 'password'}
            },
            'profile': {'required': False}
        }

    def get_fields(self):
        """
        Get the fields for the serializer.

        Returns:
            dict: A dictionary of fields for the serializer with read-only
            profile for non-staff users.
        """

        request = self.context['request']
        fields = super().get_fields()

        if request.user.is_staff:

            return fields

        else:
            fields['profile'].read_only = True

            return fields


class PrioritySerializer(serializers.ModelSerializer):
    """
    Serializer for the Priority model.
    """

    class Meta:
        model = models.Priority
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the Status model.
    """

    class Meta:
        model = models.Status
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = models.Category
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Position model.

    Attributes:
        related_category: A slug-related field representing the related category.
    """

    related_category = serializers.SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = models.Position
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.

    This serializer is designed to handle the UserProfile model with custom
    behavior such as read-only fields for non-staff users.

    Attributes:
        owner: A slug-related field representing the owner of the profile.
    """

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
        """
        Get the fields for the serializer.

        Returns:
            dict: A dictionary of fields for the serializer with read-only
            fields for non-staff users.
        """

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
    """
    Serializer for the TaskGroup model.

    This serializer handles the TaskGroup model with custom behavior such as
    read-only fields for non-staff users and non-owners.

    Attributes:
        suggested_positions: A slug-related field representing suggested positions.
        team_members: A slug-related field representing team members.
    """

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
        """
        Prevents non-staff users and non-owners from modifying certain
        fields.
        """

        request = self.context.get('request')
        fields = super().get_fields()

        if request and request.user.is_staff:
            return fields

        # Request user is object owner
        else:
            fields['assigned_task'].read_only = True

            return fields

    def to_representation(self, instance):
        """
        Prevents non-staff users from viewing tasks in which they are not
        included.
        """

        request = self.context['request']
        data = super().to_representation(instance)

        if request.user.is_staff:
            return data

        # If the request user profile is a team member of the task group.
        elif request.user.profile in instance.team_members.all():

            return data

        # For newly created instances
        return None


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    This serializer handles the Task model with custom behavior such as
    read-only fields for non-staff users and restrictions on visibility
    based on team membership.

    Attributes:
        owner: A slug-related field representing the owner of the task.
        category: A slug-related field representing the category of the task.
        priority: A slug-related field representing the priority of the task.
        status: A slug-related field representing the status of the task.
        resource_collection: A slug-related field representing the resources
                             associated with the task.
    """

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
    resource_collection = serializers.SlugRelatedField(
        queryset=models.TaskResource.objects.all(),
        many=True,
        slug_field='title',
        required=False
    )

    class Meta:
        model = models.Task
        fields = [
            'id', 'title', 'description', 'due_date', 'category', 'priority',
            'status', 'owner', 'task_group', 'resource_collection'
        ]
        extra_kwargs = {
            'task_group': {'required': False}
        }

    def get_fields(self):
        """Sets certain fields to read_only for non-staff users."""

        request = self.context.get('request')
        fields = super().get_fields()

        if request.user.is_staff:
            return fields

        else:
            fields['task_group'].read_only = True
            fields['owner'].read_only = True

            return fields

    def to_representation(self, instance):
        """Restricts users from seeing tasks in which they are not a team
        member, except for staff users.."""

        request = self.context.get('request')
        data = super().to_representation(instance)

        if request.user.is_staff:
            return data

        # Check for newly created instances
        elif not hasattr(instance.task_group, 'team_members'):
            return data

        # Not newly created
        else:
            if request.user.profile in\
                    instance.task_group.team_members.all():

                return data

        # For newly created instances
        return None


class TaskResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for the TaskResource model.

    This serializer handles the TaskResource model with custom behavior such as
    validation to ensure the user is a team member of the selected task and
    restrictions on visibility based on team membership.

    Attributes:
        id: The identifier for the TaskResource.
        source_name: The name of the source associated with the resource.
        description: A description of the resource.
        resource_link: The link to the resource.
        task: A reference to the associated task.
    """

    class Meta:
        model = models.TaskResource
        fields = [
            'id', 'source_name', 'description', 'resource_link', 'task'
        ]

    def validate(self, data):
        """
        Validate that the user is a team member of the selected task.

        This method checks if the user is a team member of the task associated
        with the submitted data. Staff users are exempt from this validation.
        """

        request = self.context['request']

        if request.user.is_staff:
            return data

        # Check if it's an update or create operation
        if 'task' in data:
            task_instance = data['task']

            # Check if the user is a team member of the selected task
            if request.user.profile not in\
                    task_instance.task_group.team_members.all():
                raise ValidationError(
                    '''The requesting user is not a member of the selected task's
                    team.'''
                )

        return data

    def to_representation(self, instance):
        """
        Restricts users from seeing task resources of tasks in which
        they are not a team member, except for staff users.

        This method ensures that only team members of the associated task can
        view the task resources, except for staff users who have unrestricted
        access.
        """

        request = self.context['request']
        data = super().to_representation(instance)

        if request.user.is_staff:

            return data

        elif request.user.profile\
                in instance.task.task_group.team_members.all():

            return data

        else:
            return None
