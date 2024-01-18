from rest_framework.test import APITestCase
from datetime import date
from django.urls import reverse
from api import serializers
from api.models import Priority, Status, Category, Position, UserProfile, \
    Task, TaskGroup
from django.contrib.auth import get_user_model
from rest_framework import status
from django.db.models.signals import post_save
from api.signals import create_task_group, create_or_update_profile


User = get_user_model()


class TestTaskModel(APITestCase):
    """Tests that are related to the task model."""

    def setUp(self) -> None:
        # Disconnect the signal during the test setup
        post_save.disconnect(create_task_group, sender=Task)
        post_save.disconnect(create_or_update_profile, sender=User)

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

        # Craeting a taskgroup instance 4
        self.task_group4 = TaskGroup.objects.create(
            name='The fourth TaskGroup'
        )
        self.task_group4.suggested_positions.set([self.position])
        self.task_group4.team_members.set([self.userprofile2])
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
        url = reverse('task-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        url = reverse('task-list')
        response = self.client.get(url)

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
        manager."""

        # Connect the signal for the current test method
        post_save.connect(create_task_group, sender=Task)

        self.client.force_authenticate(user=self.user2)
        self.user2.profile.position.is_task_manager = True
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

    def test_non_task_manager_cant_access_create(self):
        """Tests if the create view action disallows non task
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

    def test_non_staff_cant_access_create(self):
        """Tests if the create view action diallows non staff users."""

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

        # Check if the permission is denied for non staff users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_gets_assigned_to_task_when_not_yet_set(self):
        """Tests if the task view sets the request user profile to the newly
        created task as owner."""

        self.user2.profile.position.is_task_manager = True
        url = reverse('task-list')
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        self.client.force_authenticate(self.user2)
        response = self.client.post(url, data, format='json')

        task_id = response.data['id']
        task = Task.objects.get(id=task_id)

        self.assertEqual(task.owner.id, self.user2.id)

    def test_owner_is_not_assigned_to_task_when_already_set(self):
        """Tests if the task view doesnt set the request user profile to
        the newly created task as owner when owner already exists."""

        self.user2.is_staff = True
        url = reverse('task-list')
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
            'owner': self.user.email,
        }

        self.client.force_authenticate(self.user2)
        response = self.client.post(url, data, format='json')

        task_id = response.data['id']
        task = Task.objects.get(id=task_id)

        self.assertEqual(task.owner.id, self.user.id)

    def test_unauthenticated_cant_access_create(self):
        """Tests if the create view action disallows unauthenticated."""

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

        # Check if access is denied for unauthenticated task manager
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff
        users."""

        self.user2.is_staff = True
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

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non staff users."""

        self.user2.is_staff = False
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

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_update(self):
        """Tests if the update view action allows owner."""

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

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_update(self):
        """Tests if the update view action disallows non owner."""

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

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated
        users."""

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'Partially updated task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff
        users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_partial_update(self):
        """Tests if the update view action allows owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial_update view action disallows unauthenticated
        users."""

        url = reverse('task-detail', args=[self.task.id])

        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.category.name,
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

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

    def test_non_owner_cant_access_destroy(self):
        """Tests if the destroy view action disallows non owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_destroy(self):
        """Tests if the destroy view action disallows non owner."""

        url = reverse('task-detail', args=[self.task.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializer tests
    def test_serializer_fields_read_only_staff_user(self):
        """Tests if the get fields method of the serializer is keeping each
        field writable for staff users (exept id field)."""

        # Staff user
        self.user2.is_staff = True

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.TaskSerializer(
            instance=self.task,
            context={'request': request}
        )

        fields = serializer.fields
        fields.pop('id', None)

        for field, field_instance in fields.items():
            self.assertFalse(field_instance.read_only)

    def test_serializer_fields_read_only_task_manager(self):
        """Tests if the get fields method of the taskserializer is setting
        certain fields to read only for task managers."""

        # Task manager user
        self.user.is_task_manager = True

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.TaskSerializer(
            instance=self.task,
            context={'request': request}
        )

        fields = serializer.fields
        read_only_fields = ['id', 'task_group', 'owner']

        for field, field_instance in fields.items():
            # Checks if all fields expected to be read only true are correct
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)
            # Checks if all fields expected to be read only false are correct
            else:
                self.assertFalse(field_instance.read_only)

    def test_serializer_restricted_representation_staff_user(self):
        """Tests if the to representation method of the taskserializer is
        restricting certain fields from being presented for staff users."""

        self.user2.is_staff = True
        url = reverse('task-list')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        tasks = Task.objects.all()
        serializer = serializers.TaskSerializer(
            instance=tasks,
            many=True,
            context={'request': request}
        )

        representation_data = serializer.data

        # Converting ordered_dict into dict for convenience
        representation_data = [
            dict(ordered_dict) for ordered_dict in representation_data
        ]

        # The representation_data should contain all data
        expected_data = [
            {
                'id': self.task.id,
                'title': self.task.title,
                'description': self.task.description,
                'due_date': str(self.task.due_date),
                'category': self.category.name,
                'priority': self.priority.caption,
                'status': self.status.caption,
                'owner': str(self.userprofile.email),
                'task_group': self.task_group.id,
            },
            {
                'id': self.task3.id,
                'title': self.task3.title,
                'description': self.task3.description,
                'due_date': str(self.task3.due_date),
                'category': self.category.name,
                'priority': self.priority.caption,
                'status': self.status.caption,
                'owner': str(self.userprofile3.email),
                'task_group': self.task_group3.id,
            }
        ]

        self.assertEqual(representation_data, expected_data)

        # Example of missing data to double-check
        false_data = [
            {},
            {
                'id': self.task3.id,
                'title': self.task3.title,
                'description': self.task3.description,
                'due_date': str(self.task3.due_date),
                'category': self.category.name,
                'priority': 'wrong',
                'status': self.status.caption,
                'owner': str(self.userprofile3.email),
                'task_group': self.task_group3.id,
            }
        ]

        self.assertNotEqual(representation_data, false_data)

    def test_serializer_restricted_representation_non_staff_user(self):
        """Tests if the to representation method of the taskserializer is
        restricting certain fields from being presented for non-staff users."""

        self.user3.is_staff = False

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        tasks = Task.objects.all()
        # Assertion for non-staff user begins here
        serializer = serializers.TaskSerializer(
            tasks,
            many=True,
            context={'request': request}
        )

        representation_data = serializer.data

        # Converting ordered_dict into dict for convenience
        representation_data = [
            dict(ordered_dict) for ordered_dict in representation_data
        ]

        # The representation_data should miss certain data
        expected_data = [
            {},
            {
                'id': self.task3.id,
                'title': self.task3.title,
                'description': self.task3.description,
                'due_date': str(self.task3.due_date),
                'category': self.category.name,
                'priority': self.priority.caption,
                'status': self.status.caption,
                'owner': str(self.userprofile3.email),
                'task_group': self.task_group3.id,
            }
        ]

        self.assertEqual(representation_data,
                         expected_data)

        # Example of complete data for double-check
        false_data = [
            {
                'id': self.task.id,
                'title': self.task.title,
                'description': self.task.description,
                'due_date': str(self.task.due_date),
                'category': self.category.name,
                'priority': self.priority.caption,
                'status': 'wrong',
                'owner': str(self.userprofile.email),
                'task_group': self.task_group.id,
            },
            {
                'id': self.task3.id,
                'title': self.task3.title,
                'description': self.task3.description,
                'due_date': str(self.task3.due_date),
                'category': self.category.name,
                'priority': 'wrong',
                'status': self.status.caption,
                'owner': str(self.userprofile3.email),
                'task_group': self.task_group3.id,
            }
        ]

        self.assertNotEqual(representation_data, false_data)

    def test_serializer_slug_related_fields(self):
        """Tests if the task serializer is correctly setting certain fields
        to a slug field for all users."""

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.TaskSerializer(
            instance=self.task,
            context={'request': request}
        )

        data = serializer.data

        expected_data = {
            'owner': 'peterpahn@gmail.com',
            'category': 'Human Resource Management',
            'priority': 'High Priority',
            'status': 'In Progress'
        }

        # Checks if the slugfields are occupied with the correct values
        for field in expected_data:
            self.assertEqual(data[field], expected_data[field])

    def test_serializer_not_required_fields(self):
        """Tests if the serializer correctly sets certain fields to not
        required for all users."""

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.TaskSerializer(
            instance=self.task,
            context={'request': request}
        )

        fields = serializer.fields

        # Checks if the task group field is set to required false
        self.assertFalse(fields['task_group'].required)
