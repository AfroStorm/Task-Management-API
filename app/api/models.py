from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
    PermissionsMixin
# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model.

    Methods:
    - create_user(email, password=None, **extra_fields): Creates a new User instance.
    - create_superuser(email, password): Creates a new User instance as a superuser.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a new User instance.

        Example:
        ```python
        # Creating a new user instance
        user = CustomUser.objects.create_user(email='user@example.com', password='password123')
        ```
        """

        normalized_email = self.normalize_email(email)
        user = self.model(
            email=normalized_email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates a new User instance as a superuser.

        Example:
        ```python
        # Creating a new superuser instance
        superuser = CustomUser.objects.create_superuser(email='admin@example.com', password='admin123')
        ```
        """

        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Represents a custom user model.

    Fields:
    - email (EmailField): The unique email address of the user.

    Related Name Relationships:
    - profile (related_name): profile instance related to the customuser.

    Example:
    ```python
    # Creating a new custom user instance
    user = CustomUser(email='user@example.com')
    user.save()

    # Creating a user profile instance related to the user
    profile = UserProfile(owner=user, first_name='Peter', last_name='Pahn')
    profile.save()
    ```

    """
    email = models.EmailField(max_length=255, unique=True)

    objects = CustomUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        """
        Returns a string representation of the user based on its email.
        """
        return f'Email: {self.email}'


class Priority(models.Model):
    """
    A tag that shows the priority of a task.

    Fields:
    - caption (CharField): The caption field contains a string (e.g., 'High Priority').

    Related Name Relationships:
    - tasks_to_prioritize (related_name): Task instances related to the priority.

    Example:
    ```python
    # Creating a new priority instance
    priority = Priority(caption='High Priority')
    priority.save()

    # Creating a task instance related to the priority
    task = Task(priority=priority, title='Example Task', description='Task description', due_date='2024-02-03')
    task.save()
    ```
    """
    caption = models.CharField(max_length=30)

    def __str__(self) -> str:
        """
        Returns a string representation of the priority based on its caption.
        """
        return f'{self.caption}'


class Status(models.Model):
    """
    A tag that shows the current status of a task.

    Fields:
    - caption (CharField): The caption field contains a string (e.g., 'In Progress').

    Related Name Relationships:
    - task_status (related_name): Task instances related to the status.

    Example:
    ```python
    # Creating a new status instance
    status = Status(caption='In Progress')
    status.save()

    # Creating a task instance related to the status
    task = Task(status=status, title='Example Task', description='Task description', due_date='2024-02-03')
    task.save()
    ```
    """
    caption = models.CharField(max_length=30)

    def __str__(self) -> str:
        """
        Returns a string representation of the status based on its caption.
        """
        return f'{self.caption}'


class Category(models.Model):
    """
    Represents the category of a task.

    Attributes:
        name (str): The name of the category (e.g., 'Information Technology').
        description (str): Further information about the category.

    Related Name Relationships:
        categorized_tasks (related_name): Related tasks in the Task model.
        position_set (related_name): Related positions in the Position model.

    Example:
    ```python
    # Creating a new category instance
    category = Category(
        name='Information Technology',
        description='Tasks related to Information Technology'
    )
    category.save()
    ```
    """
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=255, blank=True)

    def __str__(self) -> str:
        """Returns a string representation of the model based on its name."""
        return f'{self.name}'


class Position(models.Model):
    """
    Represents the position of a user within the system.

    Fields:
    - title (str): The title of the position (e.g., 'Human Resource Specialist').
    - description (str): Further information about the position.
    - task_manager (bool): When True, gives the user permission to create tasks.
    - category (ForeignKey): Foreign key relationship with the Category model as the source.

    Related Name Relationships:
    - Empty

    Example:
    ```python
    position = UserPosition(
        title='Human Resource Specialist',
        description='Responsible for managing HR tasks',
        task_manager=True,
        category='Information Technology'
    )
    position.save()
    ```
    """

    title = models.CharField(max_length=100)
    description = models.TextField()
    is_task_manager = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='positions',
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        """Shows the model in a string representation based on its
        title.
        """
        return f'{self.title}'


class UserProfile(models.Model):
    """
    A profile for each custom user.

    Fields:
    - owner (OneToOneField): Custom user instance.
    - first_name (CharField): A string (e.g., 'Peter').
    - last_name (CharField): A string (e.g., 'Pahn').
    - phone_number (IntegerField): An integer field (e.g., 017833557).
    - email (EmailField): An email field (e.g., 'peterpahn@gmail.com').
    - position (ForeignKey): Foreign key relationship with the Position model.

    Related Name Relationships:
    - task_group (related_name): task group instance related to the userprofile.

    Example:
    ```python
    # Creating a new custom user instance
    user = CustomUser(email='user@example.com')
    user.save()

    # Creating a user profile instance related to the user
    profile = UserProfile(owner=user, first_name='Peter', last_name='Pahn', phone_number=017833557, email='peterpahn@gmail.com')
    profile.save()

    # Creating a position instance
    position = Position(title='Human Resource Specialist')
    position.save()

    # Assigning the position to the user profile
    profile.position = position
    profile.save()
    ```
    """
    owner = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.IntegerField(null=True)
    email = models.EmailField(max_length=255, blank=True)

    position = models.ForeignKey(
        Position,
        on_delete=models.DO_NOTHING,
        related_name='employees',
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the user profile based on email and phone number.
        """
        return f'{self.first_name} {self.last_name}'


class TaskGroup(models.Model):
    """
    Team of employees with different positions that take on a task.

    Fields:
    - name (CharField): The name of the task group.
    - suggested_positions (ManyToManyField): Many-to-many relationship with the Position model.
    - team_members (ManyToManyField): Many-to-many relationship with the UserProfile model.

    Related Name Relationships:
    - assigned_task (related_name): Task instance related to the task group.

    Example:
    ```python
    # Creating a new task group instance
    task_group = TaskGroup(name='Development Team')
    task_group.save()

    # Creating a position instance
    position = Position(title='Software Developer')
    position.save()

    # Adding a suggested position to the task group
    task_group.suggested_positions.add(position)

    # Creating a user profile instance
    user_profile = UserProfile(owner=user, first_name='John', last_name='Doe', phone_number=017833557, email='johndoe@gmail.com')
    user_profile.save()

    # Adding a team member to the task group
    task_group.team_members.add(user_profile)

    # Creating a task instance related to the task group
    task = Task(task_group=task_group, title='Example Task', description='Task description', due_date='2024-02-03')
    task.save()
    ```

    """
    name = models.CharField(max_length=100)
    suggested_positions = models.ManyToManyField(Position)
    team_members = models.ManyToManyField(
        UserProfile,
        related_name='taskgroup_set'
    )

    def calculate_members(self):
        """
        Calculates and returns the current number of team members for the task group.
        """
        return self.team_members.count()

    def __str__(self) -> str:
        """
        Returns a string representation of the task group based on its ID and name.
        """
        return f'ID: {self.id} - Group Name: {self.name}'


class Task(models.Model):
    """
    A task with different status options.

    Fields:
    - title (CharField): The title of the task.
    - description (TextField): The description of the task.
    - due_date (DateField): The due date of the task.
    - category (ForeignKey): Foreign key relationship with the Category model.
    - priority (ForeignKey): Foreign key relationship with the Priority model.
    - status (ForeignKey): Foreign key relationship with the Status model.
    - owner (ForeignKey): Foreign key relationship with the UserProfile model.
    - task_group (OneToOneField): One-to-one relationship with the TaskGroup model.

    Related Name Relationships:
    - resource_collection (related_name): TaskResource instances related to the task.

    Example:
    ```python
    # Creating a new category instance
    category = Category(name='Development')
    category.save()

    # Creating a new priority instance
    priority = Priority(caption='High Priority')
    priority.save()

    # Creating a new status instance
    status = Status(caption='In Progress')
    status.save()

    # Creating a new user profile instance
    user_profile = UserProfile(owner=user, first_name='John', last_name='Doe', phone_number=017833557, email='johndoe@gmail.com')
    user_profile.save()

    # Creating a new task group instance
    task_group = TaskGroup(name='Development Team')
    task_group.save()

    # Creating a new task instance
    task = Task(title='Example Task', description='Task description', due_date='2024-02-03', category=category, priority=priority, status=status, owner=user_profile, task_group=task_group)
    task.save()

    # Creating a new task resource instance related to the task
    task_resource = TaskResource(source_name='Example Resource', description='Resource description', resource_link='https://example.com/resource')
    task_resource.task = task
    task_resource.save()
    ```

    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )
    owner = models.ForeignKey(
        UserProfile,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )
    task_group = models.OneToOneField(
        TaskGroup,
        on_delete=models.CASCADE,
        related_name='task',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the task based on its ID, status, and title.
        """
        return f'ID: {self.id} - Status: {self.status} - Title: {self.title}'


class TaskResource(models.Model):
    """
    A Resource of the task (image, document, website link).

    Fields:
    - source_name (CharField): The name of the resource.
    - description (TextField): The description of the resource.
    - resource_link (CharField): The link to the resource.
    - task (ForeignKey): Foreign key relationship with the Task model.

    Related Name Relationships:
    - Empty

    Example:
    ```python
    # Creating a new task resource instance
    task_resource = TaskResource(source_name='Example Resource', description='Resource description', resource_link='https://example.com/resource')
    task_resource.save()

    # Creating a new task instance related to the task resource
    task = Task(title='Example Task', description='Task description', due_date='2024-02-03')
    task.save()
    task_resource.task = task
    task_resource.save()
    ```

    """
    source_name = models.CharField(max_length=100)
    description = models.TextField()
    resource_link = models.CharField(max_length=500)

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the task resource based on its ID and source name.
        """
        return f'Title: {self.source_name} ID: {self.id}'
