from rest_framework.test import APITestCase
from datetime import date
from api.serializers import TaskGroupSerializer
from django.urls import reverse
from api.models import Priority, Status, Category, Position, UserProfile, \
    Task, TaskGroup
from django.contrib.auth import get_user_model
from rest_framework import status
from django.db.models.signals import post_save
from api.signals import create_task_group


"""Tests that are related to the task group model."""

User = get_user_model()


class TestTaskGroupModel(APITestCase):
    """Tests that are related to the task group model."""

    def setUp(self) -> None:
        # Disconnect the signal during the test setup
        post_save.disconnect(create_task_group, sender=Task)

        # Creating user instance 1
        self.user = User.objects.create(
            email='peterpahn@gmail.com',
            password='blabla123.'
        )
        # Creating user instance 2
        self.user2 = User.objects.create(
            email='tinaturner@gmail.com',
            password='blabla123.'
        )

        # Creating user instance 3
        self.user3 = User.objects.create(
            email='captaincook@gmail.com',
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

        # Creating userprofile instance 1
        self.userprofile = UserProfile.objects.create(
            owner=self.user,
            first_name='Peter',
            last_name='Pahn',
            phone_number=int('0163557799'),
            email=self.user.email,
            position=self.position
        )

        # Creating userprofile instance 2
        self.userprofile2 = UserProfile.objects.create(
            owner=self.user2,
            first_name='Tina',
            last_name='Turner',
            phone_number=int('0176559934'),
            email=self.user2.email,
            position=self.position
        )

        # Creating userprofile instance 3
        self.userprofile3 = UserProfile.objects.create(
            owner=self.user3,
            first_name='Captain',
            last_name='Cook',
            phone_number=int('0176577922'),
            email=self.user3.email,
            position=self.position
        )

        # Craeting a taskgroup instance
        self.task_group = TaskGroup.objects.create(
            name='The first TaskGroup'
        )
        self.task_group.suggested_positions.set([self.position])
        self.task_group.team_members.set([self.userprofile])

        # Craeting a taskgroup instance 3
        self.task_group3 = TaskGroup.objects.create(
            name='The second TaskGroup'
        )
        self.task_group3.suggested_positions.set([self.position])
        self.task_group3.team_members.set([self.userprofile3])

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

        # Creating a task instance and assigning it to user3
        self.task3 = Task.objects.create(
            title='The second Task',
            description='The second task to be tested.',
            due_date=date(2023, 1, 16),
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile3,
            task_group=self.task_group3
        )

# List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('taskgroup-list')

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        url = reverse('taskgroup-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_can_access_create(self):
        """Tests if the create view action allows staff users."""

        self.client.force_authenticate(user=self.user)
        self.user.is_staff = True

        new_task = Task.objects.create(
            title='The new Task',
            description='The new task to be tested.',
            due_date=date(2023, 1, 20),
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile,
        )
        url = reverse('taskgroup-list')
        data = {
            'name': 'The first TaskGroup',
            'suggested_positions': [self.position.title],
            'team_members': [self.userprofile.email],
            'assigned_task': new_task.id
        }

        response = self.client.post(url, data, format='json')

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_cant_access_create(self):
        """Tests if the create view action diallows non staff users."""

        self.user.is_staff = False
        self.client.force_authenticate(user=self.user)

        new_task = Task.objects.create(
            title='The new Task',
            description='The new task to be tested.',
            due_date=date(2023, 1, 20),
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile,
        )
        url = reverse('taskgroup-list')
        data = {
            'name': 'The first TaskGroup',
            'suggested_positions': [self.position.title],
            'team_members': [self.userprofile.email],
            'assigned_task': new_task.id
        }

        response = self.client.post(url, data, format='json')
        print(response.content)

        # Check if the permission is denied for non staff users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskgroup-detail', args=[self.task_group.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskgroup-detail', args=[self.task_group.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskgroup-detail', args=[self.task_group.id])

        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.position.title],
            'team_members': [self.userprofile.email],
            'assigned_task': self.task.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action allows staff
        users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskgroup-detail', args=[self.task_group.id])

        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.position.title],
            'team_members': [self.userprofile.email],
            'assigned_task': self.task.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskgroup-detail', args=[self.task_group.id])

        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.position.title],
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff
        users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskgroup-detail', args=[self.task_group.id])

        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.position.title],
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
