from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from api import models, serializers, signals
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.urls import reverse


User = get_user_model()


class TestsTaskResourceModel(APITestCase):
    """Tests that are related to the TaskResource model."""

    def setUp(self) -> None:

        # Disconnect the signal during the test setup
        post_save.disconnect(signals.create_or_update_profile, sender=User)
        post_save.disconnect(signals.create_task_group, sender=models.Task)

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
        self.priority = models.Priority.objects.create(caption=caption)

        # Status instance
        caption = 'In Progress'
        self.status = models.Status.objects.create(caption=caption)

        # Category instance
        self.category = models.Category.objects.create(
            name='Human Resource Management',
            description='Human Resource Management task category involves'
            'overseeing recruitment, employee development, performance'
            'evaluation, and maintaining a positive workplace culture to'
            'optimize the organizations human capital.'
        )

        # Position instance
        self.position = models.Position.objects.create(
            title='Human Resource Specialist',
            description='A Human Resource Specialist focuses on recruitment,'
            'employee relations, benefits administration, and workforce'
            'planning, ensuring effective management of human resources'
            'within an organization.',
            is_task_manager=False,
            related_category=self.category
        )

        # Creating userprofile instance 1
        self.userprofile = models.UserProfile.objects.create(
            owner=self.user,
            first_name='Peter',
            last_name='Pahn',
            phone_number=int('0163557799'),
            email=self.user.email,
            position=self.position
        )

        # Creating userprofile instance 2
        self.userprofile2 = models.UserProfile.objects.create(
            owner=self.user2,
            first_name='Tina',
            last_name='Turner',
            phone_number=int('0176559934'),
            email=self.user2.email,
            position=self.position
        )

        # Creating userprofile instance 3
        self.userprofile3 = models.UserProfile.objects.create(
            owner=self.user3,
            first_name='Captain',
            last_name='Cook',
            phone_number=int('0176577922'),
            email=self.user3.email,
            position=self.position
        )

        # Creating a taskgroup instance
        self.task_group = models.TaskGroup.objects.create(
            name='The first TaskGroup'
        )
        self.task_group.suggested_positions.set([self.position])
        self.task_group.team_members.set([self.userprofile])

        # Creating a taskgroup instance 2
        self.task_group2 = models.TaskGroup.objects.create(
            name='The second TaskGroup'
        )
        self.task_group2.suggested_positions.set([self.position])
        self.task_group2.team_members.set([self.userprofile3])

        # Creating a task instance
        self.task = models.Task.objects.create(
            title='The first Task',
            description='The task to be tested.',
            due_date=date(2023, 1, 15),
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile,
            task_group=self.task_group
        )

        # Creating a task instance 2
        self.task2 = models.Task.objects.create(
            title='The second Task',
            description='The task to be tested.',
            due_date=date(2023, 1, 15),
            category=self.category,
            priority=self.priority,
            status=self.status,
            owner=self.userprofile3,
            task_group=self.task_group2
        )

        # Creating a task resource instance
        self.task_resource = models.TaskResource.objects.create(
            source_name='Some Image',
            description='Some descripion text for the instance',
            resource_link='https://www.example.com/sample-page',
            task=self.task
        )

        # Creating a task resource instance 2
        self.task_resource2 = models.TaskResource.objects.create(
            source_name='Another Image',
            description='Another descripion text for the instance',
            resource_link='https://www.example.com/sample-page',
            task=self.task2
        )

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('taskresource-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        url = reverse('taskresource-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('taskresource-detail',
                      args=[self.task_resource.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        url = reverse('taskresource-detail',
                      args=[self.task_resource.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_authenticated_user_can_access_create(self):
        """Tests if the create view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)

        url = reverse('taskresource-list')
        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.post(url, data, format='json')

        # Check if the task resource was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cant_access_create(self):
        """Tests if the create view action disallows unauthenticated users.
        """

        url = reverse('taskresource-list')
        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.post(url, data, format='json')

        # Check if the task resource was created
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_can_access_create(self):
        """Tests if the create view action allows staff users."""

        self.user.is_staff = True
        self.client.force_authenticate(user=self.user)

        url = reverse('taskresource-list')
        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.post(url, data, format='json')

        # Check if the task resource was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Update view
    def test_task_team_member_can_access_update(self):
        """Tests if the update view action allows task team members."""

        # User instance is in task.task_group.team_members
        self.client.force_authenticate(user=self.user)
        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_task_team_member_cant_access_update(self):
        """Tests if the update view action disallows non-task team members.
        """

        self.client.force_authenticate(user=self.user2)
        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated users.
        """

        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_task_team_member_can_access_partial_update(self):
        """Tests if the partial update action allows task team members."""

        # User instance is in task.task_group.team_members
        self.client.force_authenticate(user=self.user)
        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': 'Partially updated descripion text for the instance',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_task_team_member_cant_access_partial_update(self):
        """Tests if the partial update action disallows non-task team members.
        """

        self.client.force_authenticate(user=self.user2)
        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': 'Partially updated descripion text for the instance',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_access_partial_update(self):
        """Tests if the partial update action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': 'Partially updated descripion text for the instance',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial update view action disallows unauthenticated users.
        """

        url = reverse('taskresource-detail', args=[self.task_resource.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': 'Partially updated descripion text for the instance',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_task_team_member_can_access_destroy(self):
        """Tests if the destroy view action allows task team members."""

        # User instance is in task.task_group.team_members
        self.client.force_authenticate(user=self.user)
        url = reverse('taskresource-detail', args=[self.task_resource.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_task_team_member_cant_access_destroy(self):
        """Tests if the destroy view action disallows non-task team members.
        """

        self.client.force_authenticate(user=self.user2)
        url = reverse('taskresource-detail', args=[self.task_resource.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('taskresource-detail', args=[self.task_resource.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_user_cant_access_destroy(self):
        """Tests if the destroy view action disallows unauthenticated users.
        """

        url = reverse('taskresource-detail', args=[self.task_resource.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializer
    def test_serializer_unrestricted_representation_staff_user(self):
        """Tests if the to representation method of the taskresource 
        serializer is granting unrestricted access to staff users."""

        # Staff User
        self.user2.is_staff = True

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(url, format='json')
        request = response.wsgi_request

        task_resources = models.TaskResource.objects.all()
        serializer = serializers.TaskResourceSerializer(
            task_resources,
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
                'id': self.task_resource.id,
                'source_name': self.task_resource.source_name,
                'description': self.task_resource.description,
                'resource_link': self.task_resource.resource_link,
                'task': self.task.id

            },
            {
                'id': self.task_resource2.id,
                'source_name': self.task_resource2.source_name,
                'description': self.task_resource2.description,
                'resource_link': self.task_resource2.resource_link,
                'task': self.task2.id

            }
        ]

        self.assertEqual(representation_data, expected_data)

        # Example of missing data to double-check
        false_data = [
            {
                'id': self.task_resource.id,
                'source_name': self.task_resource.source_name,
                'description': self.task_resource.description,
                'resource_link': self.task_resource.resource_link,
                'task': self.task.id

            },
            {}
        ]

        self.assertNotEqual(representation_data, false_data)

    def test_serializer_restricted_representation(self):
        """Tests if the to representation method of the taskserializer is
        restricting certain fields from being presented for non team
        members."""

        # non-staff User

        url = reverse('task-list')
        self.client.force_authenticate(user=self.user3)

        response = self.client.get(url, format='json')
        request = response.wsgi_request

        task_resources = models.TaskResource.objects.all()
        serializer = serializers.TaskResourceSerializer(
            task_resources,
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
            {},
            {
                'id': self.task_resource2.id,
                'source_name': self.task_resource2.source_name,
                'description': self.task_resource2.description,
                'resource_link': self.task_resource2.resource_link,
                'task': self.task2.id

            }
        ]

        self.assertEqual(representation_data, expected_data)

        # Example of missing data to double-check
        false_data = [
            {
                'id': self.task_resource.id,
                'source_name': self.task_resource.source_name,
                'description': self.task_resource.description,
                'resource_link': self.task_resource.resource_link,
                'task': self.task.id

            },
            {
                'id': self.task_resource2.id,
                'source_name': self.task_resource2.source_name,
                'description': self.task_resource2.description,
                'resource_link': self.task_resource2.resource_link,
                'task': self.task2.id

            }
        ]

        self.assertNotEqual(representation_data, false_data)
