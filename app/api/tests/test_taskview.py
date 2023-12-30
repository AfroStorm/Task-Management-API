from rest_framework.test import APITestCase
from datetime import date
from api.serializers import TaskSerializer
from django.urls import reverse
from api.models import Priority, Status, Category, Position, UserProfile, \
    Task, TaskGroup
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class TestTaskVIew(APITestCase):
    """Tests the permissions of the task view."""

    def setUp(self) -> None:

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

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        response = self.client.get('http://localhost:8000/api/tasks/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        response = self.client.get('http://localhost:8000/api/tasks/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        url = reverse('task-detail', args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_task_manager_can_access_create(self):
        """Tests if the create view action allows authenticated task
        manager and, if the taskgroup is created, and if the taskgroup and
        the owner are set to the newly created task."""

        self.client.force_authenticate(user=self.user)
        self.user.profile.position.is_task_manager = True
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

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the assigned taskgroup was created
        task_group_id = response.data["task_group"]
        task_group = TaskGroup.objects.get(id=task_group_id)
        self.assertIsNotNone(task_group)

        # Check if the assigned owner was created
        owner_email = response.data['owner']
        user = User.objects.get(email=owner_email)
        owner = UserProfile.objects.get(owner=user.id)
        self.assertIsNotNone(owner)

    def test_none_task_manager_cant_access_create(self):
        """Tests if the create view action disallows none task
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

    def test_unauthorized_cant_access_create(self):
        """Tests if the create view action disallows unauthorized."""

        self.user.profile.position.is_task_manager = True
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

        # Check if access is denied for unauthorized task manager
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_can_access_create(self):
        """Tests if the create view action allows staff users."""

        self.client.force_authenticate(user=self.user)
        self.user.is_staff = True

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

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_none_staff_cant_access_create(self):
        """Tests if the create view action diallows none staff users."""

        self.client.force_authenticate(user=self.user)
        self.user.is_staff = False

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

        # Check if the permission is denied for none staff users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Update , partial update
    def test_staff_can_access_update_and_partial_update(self):
        """Tests if the update , partial_update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        # Partial update / update
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Destroy
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_none_staff_cant_access_update_and_partial_update(self):
        """Tests if the update , partial_update view action disallows
        none staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        # Partial update / update
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_update_and_partial_update(self):
        """Tests if the update , partial_update view action allows instance
        owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        # Partial update / update
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_none_owner_cant_access_update_and_partial_update(self):
        """Tests if the update , partial_update and destroy view action
        disallows instance owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update_and_partial_update(self):
        """Tests if the update , partial_update and destroy view action
        disallows unauthenticated users."""

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_none_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows none staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_destroy(self):
        """Tests if the destroy view action allows owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_none_owner_cant_access_destroy(self):
        """Tests if the destroy view action disallows none owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_serializer_get_fields_method(self):
        """Tests if the get_fields method of the taskserializer is setting
        certain fields to read-only, depending on whether the user is staff
        or not."""

        def assert_fields_read_only(user, url, fields_to_assert):
            """Sets up the serializer and assertion logic."""

            self.client.force_authenticate(user=user)
            response = self.client.get(url, format='json')
            request = response.wsgi_request

            serializer = TaskSerializer(
                instance=self.task,
                context={'request': request}
            )

            fields = serializer.fields

            for field in fields_to_assert:
                self.assertEqual(fields[field].read_only,
                                 fields_to_assert[field])

        url = reverse('task-detail', args=[self.task.id])

        # Staff users have all fields unchanged
        self.user.is_staff = True
        assert_fields_read_only(
            self.user,
            url,
            fields_to_assert={'id': True}
        )

        # Authenticated users have owner and task_group field read-only true
        self.user.is_staff = False
        assert_fields_read_only(
            self.user,
            url,
            fields_to_assert={
                'id': True,
                'owner': True,
                'task_group': True
            }
        )
