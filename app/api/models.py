from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
    PermissionsMixin
# Create your models here.


class CustomUserManager(BaseUserManager):
    """Manager for the CustomUser model."""

    def create_user(self, email, password=None, **extra_fields):
        """Creates a new User instance."""

        normalized_email = self.normalize_email(email)
        user = self.model(
            email=normalized_email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates a new User instance as a superuser."""

        user = self.create_user(
            email=email,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """A custom user model."""

    email = models.EmailField(max_length=255, unique=True)

    objects = CustomUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return f'Email: {self.email}; Username: {self.username}'


class Priority(models.Model):
    """A tag that declares the priority of a task."""

    caption = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f'{self.caption}'


class Status(models.Model):
    """A tag that shows the current status of a task."""
    caption = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f'{self.caption}'


class Category(models.Model):
    """A category for each task."""

    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f'{self.name}'


class Position(models.Model):
    """Describes the position/role of a user/team member."""
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self) -> str:
        return f'{self.title}'


class Task(models.Model):
    """A task with different status options."""

    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()

    category = models.OneToOneField(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='category_task_field'
    )
    priority = models.OneToOneField(
        Priority,
        on_delete=models.DO_NOTHING,
        related_name='priority_task_field'
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.DO_NOTHING,
        related_name='status_task_field'
    )

    def calculate_members(self):
        """Calculates and returns the current number of team members for the
        task.
        """

        pass

    def __str__(self) -> str:
        return f'ID: {self.id} - Status: {self.status} - Title: {self.title}'


class UserProfile(models.Model):
    """A profile for each user."""
    owner = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.IntegerField()

    position = models.ForeignKey(
        Position,
        on_delete=models.DO_NOTHING,
        related_name='position_userprofile_field'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.DO_NOTHING,
        related_name='task_userprofile_field'
    )
