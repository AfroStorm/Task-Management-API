from rest_framework.test import APITestCase
from datetime import date
from django.urls import reverse
from api.models import Priority, Status, Category, Position, UserProfile, \
    Task, TaskGroup
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class TestTaskVIew(APITestCase):
    """Tests the permissions of the task view."""

    def setUp(self) -> None:

        # Creating a user instance
        self.user = User.objects.create(
            email='peterpahn@gmail.com',
            password='blabla123.'
        )

        # Priority instance
        caption = 'High Priority'
        self.priority = Priority.objects.create(caption=caption)

        # Status instance
        caption = 'In Progress'
        self.status = Status.objects.create(caption=caption)

        # Category instance
        self.category = Category.objects.create(
            name='Human Resource Management',
            description='Human Resource Management task category involves'
            'overseeing recruitment, employee development, performance'
            'evaluation, and maintaining a positive workplace culture to'
            'optimize the organizations human capital.'
        )

        # Position instance
        self.position = Position.objects.create(
            title='Human Resource Specialist',
            description='A Human Resource Specialist focuses on recruitment,'
            'employee relations, benefits administration, and workforce'
            'planning, ensuring effective management of human resources'
            'within an organization.',
            is_task_manager=False,
            related_category=self.category
        )

        # Creating a userprofile instance
        self.userprofile = UserProfile.objects.create(
            owner=self.user,
            first_name='Peter',
            last_name='Pahn',
            phone_number=int('0163557799'),
            email=self.user.email,
            position=self.position
        )

        # Craeting a taskgroup instance
        self.task_group = TaskGroup.objects.create(
            name='The first TaskGroup'
        )
        self.task_group.sought_after_positions.set([self.position])
        self.task_group.team_members.set([self.userprofile])

        # Creating a task instance and assigning it to user
        self.task = Task.objects.create(
            title='The first Task',
            description='The task to be tested.',
            due_date=date(2023, 1, 15),
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile,
            task_group=self.task_group
        )

    # SAFE MEHODS
    # def test_authenticated_user_can_access_list(self):
    #     """Tests if the list view action allows authenticated users."""

    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('http://localhost:8000/api/tasks/')

    #     print(response.status_code)
    #     print(response.content)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_unauthenticated_user_cant_access_list(self):
    #     """Tests if the list view action disallows unauthenticated users."""

    #     response = self.client.get('http://localhost:8000/api/tasks/')

    #     print(response.status_code)
    #     print(response.content)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_authenticated_user_can_access_retrieve(self):
    #     """Tests if the retrieve view action allows authenticated users."""

    #     self.client.force_authenticate(user=self.user)
    #     url = reverse('task-detail', args=[self.task.id])
    #     response = self.client.get(url)

    #     print(response.status_code)
    #     print(response.content)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_unauthenticated_user_cant_access_retrieve(self):
    #     """Tests if the retrieve view action disallows unauthenticated users.
    #     """

    #     url = reverse('task-detail', args=[self.task.id])
    #     response = self.client.get(url)

    #     print(response.status_code)
    #     print(response.content)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # UNSAFE METHODS
    # def test_task_manager_can_access_create(self):
    #     """Tests if the create view action allows authenticated task
    #     manager and, if the taskgroup is created, and if the taskgroup and
    #     the owner are set to the newly created task."""

    #     self.client.force_authenticate(user=self.user)
    #     self.user.profile.position.is_task_manager = True
    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': date(2023, 1, 15),
    #         'category': self.category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }

    #     response = self.client.post(url, data, format='json')

    #     # Check if the task was created
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check if the assigned taskgroup was created
    #     task_group_id = response.data["task_group"]
    #     task_group = TaskGroup.objects.get(id=task_group_id)
    #     self.assertIsNotNone(task_group)

    #     # Check if the assigned owner was created
    #     owner_email = response.data['owner']
    #     user = User.objects.get(email=owner_email)
    #     owner = UserProfile.objects.get(owner=user.id)
    #     self.assertIsNotNone(owner)

    def test_none_task_manager_cant_access_create(self):
        """Tests if the create view action allows none task
        manager."""

        self.client.force_authenticate(user=self.user)
        self.user.profile.position.is_task_manager = False
        url = reverse('task-list')
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        response = self.client.post(url, data, format='json')

        # Check if permission is denied for non task manager
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
