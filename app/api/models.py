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
    username = models.CharField(max_length=50)

    objects = CustomUserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return f'Email: {self.email}; Username: {self.username}'


class Tag(models.Model):
    """A tag that declares the priority of a task."""

    caption = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f'{self.caption}'


class Category(models.Model):
    """A category for each task."""

    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f'{self.name}'


class Task(models.Model):
    """A task with different status options."""

    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()

    category = models.OneToOneField(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='the_task'
    )
    priority = models.OneToOneField(
        Tag,
        on_delete=models.DO_NOTHING,
        related_name='task'
    )

    def __str__(self) -> str:
        return f'{self.title}, ID: {self.id}'


class TaskGroup(models.Model):
    """Overview of all the users who work on a task."""

    participants = models.ManyToManyField(CustomUser)
    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='task_group'

    )

    def __str__(self) -> str:
        return f'Task ID: {self.task.id}, Group ID: {self.id}'
