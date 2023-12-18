from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework.authtoken.models import Token
from datetime import date
from api import views
from api.models import Priority, Status, Category, Position, UserProfile, \
    Task, TaskGroup
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class TestTaskVIew(TestCase):
    """Tests the permissions of the task view."""

    def setUp(self) -> None:

        # Creating a user instance
        email = 'peterpahn@gmail.com'
        password = 'blabla123.'
        self.user = User.objects.create(
            email=email,
            password=password
        )

        # Creating a user token
        self.token, created = Token.objects.get_or_create(user=self.user)

        # Priority instance
        caption = 'High Priority'
        self.priority = Priority.objects.create(caption=caption)

        # Status instance
        caption = 'In Progress'
        self.status = Status.objects.create(caption=caption)

        # Category instance
        name = 'Human Resource Management'
        description = 'Human Resource Management task category involves'\
            'overseeing recruitment, employee development, performance'\
            'evaluation, and maintaining a positive workplace culture to'\
            'optimize the organizations human capital.'
        self.category = Category.objects.create(
            name=name,
            description=description
        )

        # Position instance
        title = 'Human Resource Specialist'
        description = 'A Human Resource Specialist focuses on recruitment,'\
            'employee relations, benefits administration, and workforce'\
            'planning, ensuring effective management of human resources'\
            'within an organization.'
        is_task_manager = False
        related_category = self.category
        self.position = Position.objects.create(
            title=title,
            description=description,
            is_task_manager=is_task_manager,
            related_category=related_category
        )

        # Creating a userprofile instance
        owner = self.user
        first_name = 'Peter'
        last_name = 'Pahn'
        phone_number = int('0163557799')
        email = self.user.email
        position = self.position
        self.userprofile = UserProfile.objects.create(
            owner=owner,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            position=position
        )

        # Craeting a taskgroup instance
        name = 'The first TaskGroup'
        sought_after_position = self.position
        team_member = self.userprofile
        self.task_group = TaskGroup.objects.create(
            name=name
        )
        self.task_group.sought_after_positions.set([sought_after_position])
        self.task_group.team_members.set([team_member])

        # Creating a task instance and assigning it to user
        title = 'The first Task'
        description = 'The task to be tested.'
        due_date = date(2023, 1, 15)
        self.task = Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile,
            task_group=self.task_group,
        )

    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows only
        authenticated users."""

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = client.get('http://localhost:8000/api/tasks/')

        print(response.status_code)
        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
