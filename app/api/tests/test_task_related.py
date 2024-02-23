from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from django.utils import timezone
from api import serializers, models, signals
from django.contrib.auth import get_user_model
from rest_framework import status
from django.db.models.signals import post_save


User = get_user_model()


class TestTaskModel(APITestCase):
    """Tests that are related to the task model."""

    def setUp(self) -> None:
        '''The creation of the following instances are necessary to test the
        task view and eventual serializer, signal handler etc.'''

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
            password='blabla123.',
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
        self.status = models.Status.objects.create(caption='In Progress')

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
            category=self.human_resource_category,
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
        self.regular_userprofile2 = models.UserProfile.objects.create(
            first_name='Chris',
            last_name='Tucker',
            phone_number=int('0176339934'),
            email=self.regular_user2.email,
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
            due_date=timezone.now().date() + timezone.timedelta(days=2),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile,
            task_group=self.task_group1,
            created_at=timezone.now(),
            completed_at=None
        )
        self.task2 = models.Task.objects.create(
            title='The second Task',
            description='The task to be tested.',
            due_date=timezone.now().date() + timezone.timedelta(days=2),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile2,
            task_group=self.task_group2,
            created_at=timezone.now(),
            completed_at=None
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

    # # List view
    # def test_authenticated_user_can_access_list(self):
    #     """Tests if the list view action allows authenticated users."""

    #     # Authenticated user
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     response = self.client.get(url)

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_unauthenticated_user_cant_access_list(self):
    #     """Tests if the list view action disallows unauthenticated users."""

    #     # Unauthenticated user

    #     url = reverse('task-list')
    #     response = self.client.get(url)

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # Retrieve view
    # def test_authenticated_user_can_access_retrieve(self):
    #     """Tests if the retrieve view action allows authenticated users."""

    #     # Authenticated user
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse(
    #         'task-detail',
    #         args=[self.task1.id]
    #     )
    #     response = self.client.get(url)

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_unauthenticated_user_cant_access_retrieve(self):
    #     """Tests if the retrieve view action disallows unauthenticated users.
    #     """

    #     # Unauthenticated user

    #     url = reverse(
    #         'task-detail',
    #         args=[self.task1.id]
    #     )
    #     response = self.client.get(url)

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # Create view
    # def test_staff_can_access_create(self):
    #     """Tests if the create view action allows staff users."""

    #     # Staff user
    #     self.client.force_authenticate(user=self.admin_user)

    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.post(url, data, format='json')

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_task_manager_can_access_create(self):
    #     """Tests if the create view action allows authenticated task
    #     manager."""

    #     post_save.connect(signals.create_task_group, sender=models.Task)

    #     # Task manager (Allowed to create task instances)
    #     self.regular_user1.profile.position.is_task_manager = True
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.post(url, data, format='json')

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_non_staff_and_non_task_manager_cant_access_create(self):
    #     """Tests if the create view action disallows non staff and non task
    #     manager."""

    #     # Non-staff/non-task manager (Allowed to create task instances)
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.post(url, data, format='json')

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_unauthenticated_cant_access_create(self):
    #     """Tests if the create view action disallows unauthenticated."""

    #     # Unauthenticated user

    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.post(url, data, format='json')

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_owner_gets_assigned_to_task_when_not_yet_set(self):
    #     """Tests if the task view sets the request user profile to the newly
    #     created task as owner."""

    #     post_save.connect(signals.create_task_group, sender=models.Task)

    #     # Task manager (Allowed to create task instances)
    #     self.regular_user1.profile.position.is_task_manager = True
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.post(url, data, format='json')

    #     # Retrieve the newly created task instance
    #     task_id = response.data['id']
    #     task_instance = models.Task.objects.get(id=task_id)

    #     # Check if the owner got assigned correctly
    #     self.assertEqual(task_instance.owner.id, self.regular_user1.id)

    # def test_owner_is_not_assigned_to_task_when_already_set(self):
    #     """Tests if the task view doesnt set the request user profile to
    #     the newly created task as owner when owner already got set by the
    #     staff user."""

    #     # Staff user
    #     # Only a staff user can manually set the owner instance for a task
    #     self.client.force_authenticate(self.admin_user)

    #     url = reverse('task-list')
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #         'owner': self.regular_user1.email,
    #     }
    #     response = self.client.post(url, data, format='json')

    #     # Retrieve the newly created task instance
    #     task_id = response.data['id']
    #     task_instance = models.Task.objects.get(id=task_id)

    #     # Check if the owner got assigned correctly
    #     self.assertEqual(task_instance.owner.id, self.regular_user1.id)

    # # Update view
    # def test_staff_can_access_update(self):
    #     """Tests if the update view action allows staff
    #     users."""

    #     # Staff user
    #     self.client.force_authenticate(user=self.admin_user)

    #     url = reverse('task-detail', args=[self.task1.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.put(url, data, format='json')

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_owner_can_access_update(self):
    #     """Tests if the update view action allows owner."""

    #     # Task owner whos also a task_manager
    #     self.regular_user1.profile.position.is_task_manager = True
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-detail', args=[self.task1.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.put(url, data, format='json')

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_non_staff_and_non_owner_non_task_manager_cant_access_update(self):
    #     """Tests if the update view action disallows non staff and non task
    #     owner."""

    #     # Non-staff/non-task_manager user who's also not the object owner
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-detail', args=[self.task2.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.put(url, data, format='json')

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_unauthenticated_user_cant_access_update(self):
    #     """Tests if the update view action disallows unauthenticated
    #     users."""

    #     # Unauthenticated user

    #     url = reverse('task-detail', args=[self.task1.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #         'priority': self.priority.caption,
    #         'status': self.status.caption,
    #     }
    #     response = self.client.put(url, data, format='json')

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # Partial update view
    # def test_staff_can_access_partial_update(self):
    #     """Tests if the partial update view action allows staff
    #     users."""

    #     # Staff user
    #     self.client.force_authenticate(user=self.admin_user)

    #     url = reverse('task-detail', args=[self.task1.id])
    #     data = {
    #         'title': 'Partially updated task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #     }
    #     response = self.client.patch(url, data, format='json')

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_owner_can_access_partial_update(self):
    #     """Tests if the update view action allows owner."""

    #     # Task owner whos also a task_manager
    #     self.regular_user1.profile.position.is_task_manager = True
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-detail', args=[self.task1.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #     }
    #     response = self.client.patch(url, data, format='json')

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_non_staff_and_non_owner_non_task_manager_cant_access_partial_update(self):
    #     """Tests if the partial update view action disallows non staff and
    #     non task owner."""

    #     # Non-staff/non-task_manager user who's also not the object owner
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-detail', args=[self.task2.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #     }
    #     response = self.client.patch(url, data, format='json')

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_unauthenticated_user_cant_access_partial_update(self):
    #     """Tests if the partial_update view action disallows unauthenticated
    #     users."""

    #     # Unauthenticated user

    #     url = reverse('task-detail', args=[self.task1.id])
    #     data = {
    #         'title': 'The first Task',
    #         'description': 'The task to be tested.',
    #         'due_date': timezone.now().date() + timezone.timedelta(days=2),
    #         'category': self.human_resource_category.name,
    #     }
    #     response = self.client.patch(url, data, format='json')

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # Destroy view
    # def test_staff_can_access_destroy(self):
    #     """Tests if the destroy view action allows staff users."""

    #     # Staff user
    #     self.client.force_authenticate(user=self.admin_user)

    #     url = reverse('task-detail', args=[self.task1.id])
    #     response = self.client.delete(url)

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_owner_can_access_destroy(self):
    #     """Tests if the destroy view action allows owner. It is also required
    #     to have a position of task_mnager true."""

    #     # Task owner whos also a task_manager
    #     self.regular_user1.profile.position.is_task_manager = True
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-detail', args=[self.task1.id])
    #     response = self.client.delete(url)

    #     # Check if access is granted
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_non_staff_and_non_owner_non_task_manager_cant_access_destroy(self):
    #     """Tests if the destroy view action disallows non staff and non task
    #     owner."""

    #     # Non-staff/non-task_manager user who's also not the object owner
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-detail', args=[self.task2.id])
    #     response = self.client.delete(url)

    #     # CHeck if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_unauthenticated_cant_access_destroy(self):
    #     """Tests if the destroy view action disallows non owner."""

    #     # Unauthenticated user

    #     url = reverse('task-detail', args=[self.task1.id])
    #     response = self.client.delete(url)

    #     # Check if access is denied
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # Serializer tests
    # def test_serializer_fields_read_only_staff_user(self):
    #     """Tests if the get fields method of the serializer is keeping each
    #     field writable for staff users (exept id field)."""

    #     # Staff user
    #     self.client.force_authenticate(user=self.admin_user)

    #     url = reverse('task-list')
    #     response = self.client.get(url, format='json')
    #     request = response.wsgi_request

    #     serializer = serializers.TaskSerializer(
    #         instance=self.task1,
    #         context={'request': request}
    #     )

    #     fields = serializer.fields

    #     # List of expected read-only fields
    #     read_only_fields = ['id', 'created_at']

    #     # Check if fields are set to read-only correctly
    #     for field, field_instance in fields.items():
    #         if field in read_only_fields:
    #             self.assertTrue(field_instance.read_only)

    #         else:
    #             self.assertFalse(field_instance.read_only)

    # def test_serializer_fields_read_only_task_manager(self):
    #     """Tests if the get fields method of the taskserializer is setting
    #     certain fields to read only for task managers."""

    #     # Task manager (Allowed to create task instances)
    #     self.regular_user1.profile.position.is_task_manager = True
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     response = self.client.get(url, format='json')
    #     request = response.wsgi_request

    #     serializer = serializers.TaskSerializer(
    #         instance=self.task1,
    #         context={'request': request}
    #     )

    #     fields = serializer.fields

    #     # List of expected read-only fields
    #     read_only_fields = [
    #         'id', 'task_group', 'owner', 'created_at', 'completed_at',
    #         'status'
    #     ]

    #     # Check if fields are set to read-only correctly
    #     for field, field_instance in fields.items():
    #         if field in read_only_fields:
    #             self.assertTrue(field_instance.read_only)

    #         else:
    #             self.assertFalse(field_instance.read_only)

    # def test_serializer_unrestricted_representation_staff_user(self):
    #     """Tests if the to representation method of the taskserializer is
    #     granting unrestricted access to staff users."""

    #     # Staff user
    #     self.client.force_authenticate(user=self.admin_user)

    #     url = reverse('task-list')
    #     response = self.client.get(url, format='json')
    #     request = response.wsgi_request

    #     tasks = models.Task.objects.all()
    #     serializer = serializers.TaskSerializer(
    #         instance=tasks,
    #         many=True,
    #         context={'request': request}
    #     )

    #     representation_data = serializer.data
    #     representation_data = [dict(item) for item in representation_data]

    #     expected_data = [
    #         {
    #             'id': self.task1.id,
    #             'title': self.task1.title,
    #             'description': self.task1.description,
    #             'due_date': str(self.task1.due_date),
    #             'category': self.human_resource_category.name,
    #             'priority': self.priority.caption,
    #             'taskresource_set': [],
    #             'status': self.status.caption,
    #             'owner': str(self.regular_userprofile.email),
    #             'task_group': self.task_group1.id,
    #             'created_at': self.task1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
    #             'completed_at': None
    #         },
    #         {
    #             'id': self.task2.id,
    #             'title': self.task2.title,
    #             'description': self.task2.description,
    #             'due_date': str(self.task2.due_date),
    #             'category': self.human_resource_category.name,
    #             'priority': self.priority.caption,
    #             'taskresource_set': [],
    #             'status': self.status.caption,
    #             'owner': str(self.regular_userprofile2.email),
    #             'task_group': self.task_group2.id,
    #             'created_at': self.task2.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
    #             'completed_at': None
    #         }
    #     ]

    #     # Sorting list by its dictionaries.
    #     # lambda gets the ID of each dictionary wihin the list and provides it
    #     # as a value for the key parameter of the sorted function. By that
    #     # the order of the dictionaries of both lists is identical. Now both
    #     # representation and expected data list can be compared.
    #     representation_data = sorted(
    #         representation_data, key=lambda i: self.get_id(i)
    #     )
    #     expected_data = sorted(
    #         expected_data, key=lambda i: self.get_id(i)
    #     )

    #     # Check if representation data contains all instances
    #     self.assertEqual(representation_data, expected_data)

    #     false_data = [
    #         None,
    #         {
    #             'id': self.task1.id,
    #             'title': self.task1.title,
    #             'description': self.task1.description,
    #             'due_date': str(self.task1.due_date),
    #             'category': self.human_resource_category.name,
    #             'priority': 'wrong',
    #             'taskresource_set': [],
    #             'status': self.status.caption,
    #             'owner': str(self.regular_userprofile.email),
    #             'task_group': self.task_group1.id,
    #             'created_at': self.task1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
    #             'completed_at': None
    #         }
    #     ]

    #     # Look further up in function for explanation
    #     false_data = sorted(
    #         false_data, key=lambda i: self.get_id(i)
    #     )

    #     # Double-check with purposely wrong data
    #     self.assertNotEqual(representation_data, false_data)

    # def test_serializer_restricted_representation_non_team_member(self):
    #     """Tests if the to representation method of the taskserializer is
    #     restricting certain fields from being presented for non team
    #     members."""

    #     # Authenticated user
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     response = self.client.get(url, format='json')
    #     request = response.wsgi_request

    #     tasks = models.Task.objects.all()
    #     serializer = serializers.TaskSerializer(
    #         tasks,
    #         many=True,
    #         context={'request': request}
    #     )

    #     representation_data = serializer.data

    #     expected_data = [
    #         None,
    #         {
    #             'id': self.task1.id,
    #             'title': self.task1.title,
    #             'description': self.task1.description,
    #             'due_date': str(self.task1.due_date),
    #             'category': self.human_resource_category.name,
    #             'priority': self.priority.caption,
    #             'taskresource_set': [],
    #             'status': self.status.caption,
    #             'owner': str(self.regular_userprofile.email),
    #             'task_group': self.task_group1.id,
    #             'created_at': self.task1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
    #             'completed_at': None

    #         }
    #     ]

    #     # Sorting list by its dictionaries.
    #     # lambda gets the ID of each dictionary wihin the list and provides it
    #     # as a value for the key parameter of the sorted function. By that
    #     # the order of the dictionaries of both lists is identical. Now both
    #     # representation and expected data list can be compared.
    #     representation_data = sorted(
    #         representation_data, key=lambda i: self.get_id(i)
    #     )
    #     expected_data = sorted(
    #         expected_data, key=lambda i: self.get_id(i)
    #     )

    #     # Check if representation data contains only team member instances
    #     self.assertEqual(representation_data, expected_data)

    #     false_data = [
    #         {
    #             'id': self.task1.id,
    #             'title': self.task1.title,
    #             'description': self.task1.description,
    #             'due_date': str(self.task1.due_date),
    #             'category': self.human_resource_category.name,
    #             'priority': self.priority.caption,
    #             'taskresource_set': [],
    #             'status': 'wrong',
    #             'owner': str(self.regular_userprofile.email),
    #             'task_group': self.task_group1.id,
    #             'created_at': self.task1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
    #             'completed_at': None
    #         },
    #         {
    #             'id': self.task2.id,
    #             'title': self.task2.title,
    #             'description': self.task2.description,
    #             'due_date': str(self.task2.due_date),
    #             'category': self.human_resource_category.name,
    #             'priority': 'wrong',
    #             'taskresource_set': [],
    #             'status': self.status.caption,
    #             'owner': str(self.regular_userprofile.email),
    #             'task_group': self.task_group2.id,
    #             'created_at': self.task2.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z',
    #             'completed_at': None
    #         }
    #     ]

    #     # Look further up in function for explanation
    #     false_data = sorted(
    #         false_data, key=lambda i: self.get_id(i)
    #     )

    #     # Double-check with purposely wrong data
    #     self.assertNotEqual(representation_data, false_data)

    # def test_serializer_slug_related_fields(self):
    #     """Tests if the task serializer is correctly setting certain fields
    #     to a slug field for all users."""

    #     # Authenticated user
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     response = self.client.get(url, format='json')
    #     request = response.wsgi_request

    #     serializer = serializers.TaskSerializer(
    #         instance=self.task1,
    #         context={'request': request}
    #     )

    #     data = serializer.data

    #     expected_data = {
    #         'owner': 'peterpahn@gmail.com',
    #         'category': 'Human Resource Management',
    #         'priority': 'High Priority',
    #         'status': 'In Progress'
    #     }

    #     # Checks if the slugfields are occupied with the correct values
    #     for field in expected_data:
    #         self.assertEqual(data[field], expected_data[field])

    # def test_serializer_not_required_fields(self):
    #     """Tests if the serializer correctly sets certain fields to not
    #     required for all users."""

    #     # Authenticated user
    #     self.client.force_authenticate(user=self.regular_user1)

    #     url = reverse('task-list')
    #     response = self.client.get(url, format='json')
    #     request = response.wsgi_request

    #     serializer = serializers.TaskSerializer(
    #         instance=self.task1,
    #         context={'request': request}
    #     )

    #     fields = serializer.fields

    #     # Checks if the task group field is set to required false
    #     self.assertFalse(fields['task_group'].required)

    def test_serializer_validate_due_date_greater_than_current_date(self):
        """
        Checks if the validate_due_date method of the task serializer
        throws an error if the due_date is equal or less than the
        current date.
        """

        # Creating a Request object to pass it into the serializer
        # (conditional logik requires it)
        url = reverse('task-list')
        api_factory = APIRequestFactory()
        request = api_factory.get(url)
        request.user = self.regular_user1

        serializer = serializers.TaskSerializer(
            context={'request': request},
        )

        # --INVALID DUE_DATE--
        current_date = timezone.now()
        two_days_earlier = timezone.timedelta(days=2)
        invalid_date = current_date - two_days_earlier

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_due_date(invalid_date)

        # --VALID DUE_DATE--
        two_days_later = timezone.timedelta(days=2)
        valid_date = current_date + two_days_later

        validated_date = serializer.validate_due_date(valid_date)

        self.assertEqual(validated_date, valid_date)

    # Signal handler test
    def test_signal_handler_sets_completed_at_field_to_current_date(self):
        """
        Checks if the signal handler sets the completed_at
        datetimefield of of the task instance to the current date when
        the task status got set to completed.
        """

        # Task owner whos also a task_manager
        self.regular_user1.profile.position.is_task_manager = True
        self.client.force_authenticate(user=self.regular_user1)

        # Created a Completed status instance
        completed_status = models.Status.objects.create(
            caption="Completed"
        )

        url = reverse('task-detail', args=[self.task1.id])
        data = {
            'status': completed_status.caption
        }
        response = self.client.patch(url, data, format='json')

        # Retrieving the completed_at datetime of the task instance and
        # converting it to a date so you are able to make a comparison.
        created_at_datetime = response.data.get('created_at')

        datetime_object = timezone.datetime.fromisoformat(
            created_at_datetime[:-1]
        ).replace(tzinfo=timezone.utc)

        created_at = datetime_object.date()
        current_date = timezone.now().date()

        self.assertEqual(created_at, current_date)
