from rest_framework.test import APITestCase
from rest_framework import status
from django.forms.models import model_to_dict
from datetime import date
from api import models, serializers, signals
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.urls import reverse


User = get_user_model()


class TestsTaskResourceModel(APITestCase):
    """Tests that are related to the TaskResource model."""

    def setUp(self) -> None:
        '''The creation of the following instances are necessary to test the
        task resource view nd eventual serializer, signal handler etc.'''

        # Deactivate signal handlers for more control over setUp instances
        post_save.disconnect(signals.create_or_update_profile, sender=User)
        post_save.disconnect(signals.create_task_group, sender=models.Task)

        # Creating user instances
        self.regular_user1 = User.objects.create(
            email='peterpahn@gmail.com',
            password='blabla123.'
        )
        self.regular_user2 = User.objects.create(
            email='christucker@gmail.com',
            password='blabla123.'
        )
        self.admin_user = User.objects.create(
            email='tinaturner@gmail.com',
            password='blabla123.',
            is_staff=True
        )

        # Priority instance
        self.priority = models.Priority.objects.create(
            caption='High Priority'
        )

        # Status instance
        caption = 'In Progress'
        self.status = models.Status.objects.create(caption=caption)

        # Creating category instances
        self.human_resource_category = models.Category.objects.create(
            name='Human Resource Management',
            description='''Human Resource Management task category involves
            overseeing recruitment, employee development, performance
            evaluation, and maintaining a positive workplace culture to
            optimize the organizations human capital.'''
        )

        # Creating position instances
        self.human_resource_position = models.Position.objects.create(
            title='Human Resource Specialist',
            description='''A Human Resource Specialist focuses on
            recruitment, employee relations, benefits administration, and
            workforce planning, ensuring effective management of human
            resources within an organization.''',
            is_task_manager=False,
            category=self.human_resource_category
        )

        # Creating userprofile instances
        self.regular_userprofile = models.UserProfile.objects.create(
            owner=self.regular_user1,
            first_name='Peter',
            last_name='Pahn',
            phone_number=int('0163557799'),
            email=self.regular_user1.email,
            position=self.human_resource_position
        )
        self.admin_userprofile = models.UserProfile.objects.create(
            owner=self.admin_user,
            first_name='Tina',
            last_name='Turner',
            phone_number=int('0176559934'),
            email=self.admin_user.email,
            position=self.human_resource_position
        )
        self.regular_userprofile2 = models.UserProfile.objects.create(
            owner=self.regular_user2,
            first_name='Chris',
            last_name='Tucker',
            phone_number=int('0176339934'),
            email=self.regular_user2.email,
            position=self.human_resource_position
        )

        # Creating taskgroup instances
        # First task group
        self.task_group1 = models.TaskGroup.objects.create(
            name='The first TaskGroup'
        )
        self.task_group1.suggested_positions.set(
            [self.human_resource_position]
        )
        self.task_group1.team_members.set([self.regular_userprofile])
        # Second task group
        self.task_group2 = models.TaskGroup.objects.create(
            name='The second TaskGroup'
        )
        self.task_group2.suggested_positions.set(
            [self.human_resource_position]
        )
        self.task_group2.team_members.set([self.regular_userprofile2])

        # Creating task instances
        self.task1 = models.Task.objects.create(
            title='The first Task',
            description='The task to be tested.',
            due_date=date(2023, 1, 15),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile,
            task_group=self.task_group1
        )
        self.task2 = models.Task.objects.create(
            title='The second Task',
            description='The task to be tested.',
            due_date=date(2023, 1, 15),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile,
            task_group=self.task_group2
        )

        # Creating task resource instances
        self.task_resource1 = models.TaskResource.objects.create(
            source_name='Some Image',
            description='Some descripion text for the instance',
            resource_link='https://www.example.com/sample-page',
            task=self.task1
        )
        self.task_resource2 = models.TaskResource.objects.create(
            source_name='Another Image',
            description='Another descripion text for the instance',
            resource_link='https://www.example.com/sample-page',
            task=self.task2
        )

    # Helper functions
    def get_id(self, i):
        """
        Gets the id of a dictionary. If (i) is None returns 0 instead.
        Is used together with a lambda function in this test.
        """

        if i == None:
            return 0
        else:
            return i.get('id')

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-list')
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        # Unauthenticated user

        url = reverse('taskresource-list')
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'taskresource-detail',
            args=[self.task_resource1.id]
        )
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse(
            'taskresource-detail',
            args=[self.task_resource1.id]
        )
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_authenticated_user_can_access_create(self):
        """Tests if the create view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-list')
        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task1.id
        }
        response = self.client.post(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cant_access_create(self):
        """Tests if the create view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse('taskresource-list')
        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task1.id
        }
        response = self.client.post(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task1.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_team_member_can_access_update(self):
        """Tests if the update view action allows task team members
        (task_resource.task.task_group.team_members)."""

        # Task team member
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task1.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_task_team_member_cant_access_update(self):
        """Tests if the update view action disallows non-task team members.
        """

        # Non-task member
        self.client.force_authenticate(user=self.regular_user1)
        url = reverse('taskresource-detail', args=[self.task_resource2.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task2.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        data = {
            'source_name': 'Updated Image',
            'description': 'Updated descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task1.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': '''Partially updated descripion text for the
                instance''',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_team_member_can_access_partial_update(self):
        """Tests if the partial update action allows task team members."""

        # Task team member
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': '''Partially updated descripion text for the
                instance''',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_task_team_member_cant_access_partial_update(self):
        """Tests if the partial update action disallows non-task team members.
        """

        # Non-task team member
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-detail', args=[self.task_resource2.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': '''Partially updated descripion text for the
                instance''',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial update view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        data = {
            'source_name': 'Partially updated Image',
            'description': '''Partially updated descripion text for the
                instance''',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_team_member_can_access_destroy(self):
        """Tests if the destroy view action allows task team members."""

        # Task team member
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_task_team_member_cant_access_destroy(self):
        """Tests if the destroy view action disallows non-task team members.
        """

        # Non-task team member
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-detail', args=[self.task_resource2.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_destroy(self):
        """Tests if the destroy view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse('taskresource-detail', args=[self.task_resource1.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializer
    def test_serializer_unrestricted_representation_staff_user(self):
        """Tests if the to representation method of the taskresource
        serializer is granting unrestricted access to staff users."""

        # Staff User
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskresource-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        task_resources = models.TaskResource.objects.all()
        serializer = serializers.TaskResourceSerializer(
            task_resources,
            many=True,
            context={'request': request}
        )

        representation_data = serializer.data

        expected_data = [
            {
                'id': self.task_resource1.id,
                'source_name': self.task_resource1.source_name,
                'description': self.task_resource1.description,
                'resource_link': self.task_resource1.resource_link,
                'task': self.task1.id

            },
            {
                'id': self.task_resource2.id,
                'source_name': self.task_resource2.source_name,
                'description': self.task_resource2.description,
                'resource_link': self.task_resource2.resource_link,
                'task': self.task2.id

            }
        ]

        # Sorting list by its dictionaries.
        # lambda gets the ID of each dictionary wihin the list and provides it
        # as a value for the key parameter of the sorted function. By that
        # the order of the dictionaries of both lists is identical. Now both
        # representation and expected data list can be compared.
        representation_data = sorted(
            representation_data, key=lambda i: self.get_id(i)
        )
        expected_data = sorted(
            expected_data, key=lambda i: self.get_id(i)
        )

        # Check if representation data contains all instances
        self.assertEqual(representation_data, expected_data)

        false_data = [
            {
                'id': self.task_resource1.id,
                'source_name': self.task_resource1.source_name,
                'description': self.task_resource1.description,
                'resource_link': self.task_resource1.resource_link,
                'task': self.task1.id

            },
            None
        ]

        # Look further up in function for explanation
        false_data = sorted(
            false_data, key=lambda i: self.get_id(i)
        )

        # Double-check with purposely wrong data
        self.assertNotEqual(representation_data, false_data)

    def test_serializer_restricted_representation_non_team_member(self):
        """Tests if the to representation method of the taskserializer is
        restricting certain fields from being presented for non team
        members."""

        # non-staff User
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskresource-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        task_resources = models.TaskResource.objects.all()
        serializer = serializers.TaskResourceSerializer(
            task_resources,
            many=True,
            context={'request': request}
        )

        representation_data = serializer.data

        expected_data = [
            None,
            {
                'id': self.task_resource1.id,
                'source_name': self.task_resource1.source_name,
                'description': self.task_resource1.description,
                'resource_link': self.task_resource1.resource_link,
                'task': self.task1.id
            }
        ]

        # Sorting list by its dictionaries.
        # lambda gets the ID of each dictionary wihin the list and provides it
        # as a value for the key parameter of the sorted function. By that
        # the order of the dictionaries of both lists is identical. Now both
        # representation and expected data list can be compared.
        representation_data = sorted(
            representation_data, key=lambda i: self.get_id(i)
        )
        expected_data = sorted(
            expected_data, key=lambda i: self.get_id(i)
        )

        # Check if representation data contains only team member instances
        self.assertEqual(representation_data, expected_data)

        false_data = [
            {
                'id': self.task_resource1.id,
                'source_name': self.task_resource1.source_name,
                'description': self.task_resource1.description,
                'resource_link': self.task_resource1.resource_link,
                'task': self.task1.id

            },
            {
                'id': self.task_resource2.id,
                'source_name': self.task_resource2.source_name,
                'description': self.task_resource2.description,
                'resource_link': self.task_resource2.resource_link,
                'task': self.task2.id

            }
        ]

        # Look further up in function for explanation
        false_data = sorted(
            false_data, key=lambda i: self.get_id(i)
        )

        # Double-check with purposely wrong data
        self.assertNotEqual(representation_data, false_data)

    def test_serializer_create_method_restricts_non_team_member(self):
        """
        Checks if the create method of the serializer prevents the
        request user from assigning a task resource to a task of which
        he is not a team member.
        """

        # Creating a Request object to pass it into the serializer
        # (conditionals of the create method require it)
        attributes = {'user': self.regular_user1}
        Request = type('Request', (object,), attributes)()

        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task2.id
        }

        # Create serialization
        serializer = serializers.TaskResourceSerializer(
            data=data,
            context={'request': Request},
        )
        serializer.is_valid()

        # Check if the serializer throws a validationerror when the
        # request user tries to connect a taskresource instance to
        # a task instance of which he is not a team member
        with self.assertRaises(serializers.ValidationError):
            serializer.create(
                validated_data=serializer.validated_data
            )

    def test_serializer_update_method_restricts_non_team_member(self):
        """
        Checks if the update method of the serializer prevents the
        request user from assigning a task resource to a task of which
        he is not a team member.
        """

        # Creating a Request object to pass it into the serializer
        # (conditionals of the update method require it)
        attributes = {'user': self.regular_user1}
        Request = type('Request', (object,), attributes)()

        data = {
            'task': self.task2.id
        }

        # partial update serialization
        serializer = serializers.TaskResourceSerializer(
            data=data,
            instance=self.task_resource1,
            context={'request': Request},
            partial=True
        )
        serializer.is_valid()

        # Check if the serializer throws a validationerror when the
        # request user tries to connect a taskresource instance to
        # a task instance of which he is not a team member
        with self.assertRaises(serializers.ValidationError):
            serializer.update(
                instance=self.task_resource1,
                validated_data=serializer.validated_data
            )

    def test_serializer_create_method_staff_user(self):
        """
        Checks if the create method of the serializer allows the
        request staff user to assign a task resource to any task.
        """

        # Creating a Request object to pass it into the serializer
        # (conditionals of the update method require it)
        attributes = {'user': self.admin_user}
        Request = type('Request', (object,), attributes)()

        data = {
            'source_name': 'Another Image',
            'description': 'Another descripion text for the instance',
            'resource_link': 'https://www.example.com/sample-page',
            'task': self.task2.id
        }

        # Create serialization
        serializer = serializers.TaskResourceSerializer(
            data=data,
            context={'request': Request},
        )
        serializer.is_valid()

        created_instance = serializer.create(
            validated_data=serializer.validated_data
        )

        # Preparing the expected data for the comparison with
        # the actual updated data by first converting the task
        # resource instance  into a dictionry and then manually
        # updating the task field with the expected value
        expected_data_dict = model_to_dict(self.task_resource1)
        expected_data_dict['task'] = self.task2.id

        # Also converting the updated instance into a dict for
        # comparison
        updated_data_dict = model_to_dict(created_instance)

        self.assertEqual(updated_data_dict, expected_data_dict)

    def test_serializer_update_method_staff_user(self):
        """
        Checks if the update method of the serializer allows the
        request staff user to assign a task resource to any task.
        """

        # Creating a Request object to pass it into the serializer
        # (conditionals of the update method require it)
        attributes = {'user': self.admin_user}
        Request = type('Request', (object,), attributes)()

        data = {
            'task': self.task2.id
        }

        # partial update serializattion
        serializer = serializers.TaskResourceSerializer(
            data=data,
            instance=self.task_resource1,
            context={'request': Request},
            partial=True
        )
        serializer.is_valid()
        updated_instance = serializer.update(
            instance=self.task_resource1,
            validated_data=serializer.validated_data
        )

        # Preparing the expected data for the comparison with
        # the actual updated data by first converting the task
        # resource instance  into a dictionry and then manually
        # updating the task field with the expected value
        expected_data_dict = model_to_dict(self.task_resource1)
        expected_data_dict['task'] = self.task2.id

        # Also converting the updated instance into a dict for
        # comparison
        updated_data_dict = model_to_dict(updated_instance)

        self.assertEqual(updated_data_dict, expected_data_dict)
