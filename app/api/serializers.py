from rest_framework import serializers
from django.contrib.auth import get_user_model
from api import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

User = get_user_model()

# Modelserializer


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
                'style': {'input_type': 'password'}
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

        request = self.context.get('request')
        fields = super().get_fields()

        if request and request.user.is_staff:

            return fields

        else:
            fields['profile'].read_only = True

            return fields

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        return super().create(validated_data)


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
        category: A slug-related field representing the related category.
    """

    category = serializers.SlugRelatedField(
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

    position = serializers.SlugRelatedField(
        queryset=models.Position.objects.all(),
        slug_field='title'
    )

    class Meta:
        model = models.UserProfile
        fields = [
            'id', 'owner', 'first_name', 'last_name', 'phone_number', 'email',
            'position', 'taskgroup_set', 'task_set'
        ]
        extra_kwargs = {
            'taskgroup_set': {'required': False},
            'task_set': {'required': False},
            'owner': {'required': False}
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

        if request and request.user.is_staff:
            return fields

        else:
            read_only_fields = [
                'owner', 'taskgroup_set', 'task_set', 'position'
            ]

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
        fields = [
            'id', 'name', 'suggested_positions', 'team_members',
            'task'
        ]

    def get_fields(self):
        """
        Prevents non-staff users from modifying certain fields.
        """

        request = self.context.get('request')
        fields = super().get_fields()

        if request and request.user.is_staff:

            return fields

        else:
            fields['task'].read_only = True

            return fields

    def to_representation(self, instance):
        """
        Prevents non-staff users from viewing tasks in which they are not
        included.
        """

        request = self.context['request']
        data = super().to_representation(instance)

        if request and request.user.is_staff:

            return data

        # If the request user profile is a team member of the task group.
        elif request.user.profile in instance.team_members.all():

            return data


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
        task_resource_set: A slug-related field representing the resources
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
    taskresource_set = serializers.SlugRelatedField(
        queryset=models.TaskResource.objects.all(),
        many=True,
        slug_field='title',
        required=False
    )

    class Meta:
        model = models.Task
        fields = [
            'id', 'title', 'description', 'due_date', 'category', 'priority',
            'status', 'owner', 'task_group', 'taskresource_set',
            'completed_at', 'created_at'
        ]
        extra_kwargs = {
            'task_group': {'required': False}
        }

    def validate(self, attrs):
        """
        Checks if the due_date is not before the current
        date.
        """

        validated_data = super().validate(attrs)

        if 'due_date' in validated_data:
            if validated_data['due_date'] != None:

                current_date = timezone.now().date()
                due_date = validated_data['due_date']

                if due_date <= current_date:
                    raise ValidationError(
                        '''
                        The due_date cant be less or equal to the current date
                        '''
                    )

        return validated_data

    def get_fields(self):
        """Sets certain fields to read_only for non-staff users."""

        request = self.context.get('request')
        fields = super().get_fields()

        if request and request.user.is_staff:
            return fields

        else:
            fields['task_group'].read_only = True
            fields['owner'].read_only = True
            fields['created_at'].read_only = True
            fields['status'].read_only = True
            fields['completed_at'].read_only = True

            return fields

    def to_representation(self, instance):
        """Restricts users from seeing tasks in which they are not a team
        member, except for staff users.."""

        request = self.context.get('request')
        data = super().to_representation(instance)

        if request and request.user.is_staff:
            return data

        else:
            if request.user.profile in\
                    instance.task_group.team_members.all():

                return data


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
        extra_kwargs = {
            'resource_link': {'required': False},
        }

    def validate(self, attrs):
        """
        Prevents users from assigning task resourcess to tasks of
        which they are not a team member.

        This method checks if the user is a team member of the task associated
        with the submitted data. Staff users are exempt from this validation.
        """

        validated_data = super().validate(attrs)
        request = self.context.get('request')

        if request and request.user.is_staff:
            return validated_data

        # Check if the submitted data contains an actual task instance
        # to either update or create a task resource instance.
        if request and 'task' in validated_data:
            task_instance = validated_data['task']

            # Check if the user is a team member of the selected task
            if request.user.profile not in\
                    task_instance.task_group.team_members.all():
                raise ValidationError(
                    '''The requesting user is not a member of the selected task's
                    team.'''
                )

        return validated_data

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

        if request and request.user.is_staff:

            return data

        elif request.user.profile\
                in instance.task.task_group.team_members.all():

            return data


# Customserializer
class StatusChangeSerializer(serializers.Serializer):
    """
    A custom serializer for the change_status view action of the task
    view.
    """

    status = serializers.ChoiceField(
        choices=['In Progress', 'Postponed', 'Archived', 'Completed']
    )
    due_date = serializers.DateTimeField(required=False)
    completed_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        """
        Checks if the validated data is in the correct relationship
        to each other and if the due_date is set up correctly
        (not before or equal to current date).
        """

        validated_data = super().validate(attrs)
        status = validated_data.get('status')

        # Certain statuses can only come with specific date fields
        # (e.g. {"status": "In Progress"},{"due_date": "datetime"},
        # {"status": "Completed"},{"ducompleted_ate_date": "datetime"})
        if status in ['In Progress', 'Postponed']:
            if 'due_date' not in validated_data:
                raise serializers.ValidationError(
                    '''
                    The 'due_date' field is required for 'In Progress' or
                    'Postponed' status.
                    '''
                )

        elif status == 'Archived':
            if 'due_date' in validated_data and \
                    validated_data.get('due_date') is not None:
                raise serializers.ValidationError(
                    '''
                    The 'due_date' field should be None for 'Archived' status.
                    '''
                )

        elif status == 'Completed':
            if 'completed_at' not in validated_data:
                raise serializers.ValidationError(
                    '''
                    The 'completed_at' field is required for 'Completed' 
                    status.
                    '''
                )

        # The due_date cant be equal or less to the current_date
        if 'due_date' in validated_data and \
                validated_data.get('due_date') is not None:

            current_date = timezone.now().date()
            due_date = validated_data.get('due_date')

            if due_date <= current_date:
                raise ValidationError(
                    '''
                    The due_date cant be less or equal to the current_date
                    '''
                )

        return validated_data

    def update(self, instance, validated_data):
        """
        Updates the fields of the task instance.
        """
        instance.status = validated_data.get('status')
        instance.due_date = validated_data.get('due_date')
        instance.completed_at = validated_data.get('completed_at')
        instance.save()

        return instance
