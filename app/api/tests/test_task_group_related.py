from rest_framework.test import APITestCase
from datetime import date
from api.serializers import TaskGroupSerializer
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.db.models.signals import post_save
from api import signals, models


User = get_user_model()


class TestTaskGroupModel(APITestCase):
    """Tests that are related to the task group model."""

    def setUp(self) -> None:
        '''The creation of the following instances are necessary to test the
        task group view and eventual serializer, signal handler etc.'''

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
        # Thrid task group
        self.task_group3 = models.TaskGroup.objects.create(
            name='The third TaskGroup'
        )
        self.task_group3.suggested_positions.set(
            [self.human_resource_position]
        )
        self.task_group3.team_members.set([self.admin_userprofile])

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
            owner=self.regular_userprofile2,
            task_group=self.task_group2
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

        url = reverse('taskgroup-list')
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        # Unauthenticated user

        url = reverse('taskgroup-list')
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'taskgroup-detail',
            args=[self.task_group1.id]
        )
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse(
            'taskgroup-detail',
            args=[self.task_group1.id]
        )
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_can_access_create(self):
        """Tests if the create view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        # Creating task instance
        new_task = models.Task.objects.create(
            title='The new Task',
            description='The new task to be tested.',
            due_date=date(2023, 1, 20),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile,
        )

        url = reverse('taskgroup-list')
        data = {
            'name': 'The first TaskGroup',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': new_task.id
        }

        response = self.client.post(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_cant_access_create(self):
        """Tests if the create view action disallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        # Creating task instance
        new_task = models.Task.objects.create(
            title='The new Task',
            description='The new task to be tested.',
            due_date=date(2023, 1, 20),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile,
        )

        url = reverse('taskgroup-list')
        data = {
            'name': 'The first TaskGroup',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': new_task.id
        }
        response = self.client.post(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_create(self):
        """Tests if the create view action diallows unauthenticated users."""

        # Unauthenticated user

        # Creating task instance
        new_task = models.Task.objects.create(
            title='The new Task',
            description='The new task to be tested.',
            due_date=date(2023, 1, 20),
            category=self.human_resource_category,
            priority=self.priority,
            status=self.status,
            owner=self.regular_userprofile,
        )

        url = reverse('taskgroup-list')
        data = {
            'name': 'The first TaskGroup',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': new_task.id
        }
        response = self.client.post(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': self.task1.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_access_update(self):
        """Tests if the update view action allows task owner."""

        # Task object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': self.task1.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action disallows staff users."""

        # Non-staff user who's also not the object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group2.id])
        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': self.task2.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_cant_access_update(self):
        """Tests if the update view action disallows non owner."""

        # Non-task owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group2.id])
        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': self.task2.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated
        users."""

        # Unauthenticated user

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        data = {
            'name': 'Updated task group',
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email],
            'task': self.task1.id
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.human_resource_position.title]
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff
        users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group2.id])
        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.human_resource_position.title],
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_partial_update(self):
        """Tests if the partial update view action allows owner."""

        # Task owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.human_resource_position.title],
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_partial_update(self):
        """Tests if the partial update view action disallows owner."""

        # Non-task owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group2.id])
        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.human_resource_position.title],
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_partial_update(self):
        """Tests if the partial update view action disallows staff
        users."""

        # Unauthenticated user

        url = reverse('taskgroup-detail', args=[self.task_group1.id])

        data = {
            'name': 'Partially updated task group',
            'suggested_positions': [self.human_resource_position.title],
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskgroup-detail', args=[self.task_group3.id])
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_destroy(self):
        """Tests if the destroy view action disallows unauthenticated
        users."""

        # Unauthenticated user

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializer
    def test_fields_read_only_staff_user(self):
        """Tests if the get_fields method of the taskserializer is setting
        only the id field to read-only for staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = TaskGroupSerializer(
            instance=self.task_group1,
            context={'request': request}
        )

        fields = serializer.fields

        # List of expected read-only fields
        read_only_fields = ['id']

        # Check if fields are set to read-only correctly
        for field, field_instance in fields.items():
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)

            else:
                self.assertFalse(field_instance.read_only)

    def test_owner_fields_read_only(self):
        """Tests if the get_fields method of the taskserializer is setting
        certain fields to read-only for for the owner."""

        # Task owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = TaskGroupSerializer(
            instance=self.task_group1,
            context={'request': request}
        )

        fields = serializer.fields

        # List of expected read-only fields
        read_only_fields = ['id', 'task']

        # Check if fields are set to read-only correctly
        for field, field_instance in fields.items():
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)

            else:
                self.assertFalse(field_instance.read_only)

    def test_staff_gets_unrestricted_representation(self):
        """Tests if the to_representation method of the taskgroupserializer is
        granting full representation to each task."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('taskgroup-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        queryset = models.TaskGroup.objects.all()
        serializer = TaskGroupSerializer(
            instance=queryset,
            many=True,
            context={'request': request}
        )

        representation_data = serializer.data

        expected_data = [
            {
                'id': self.task_group1.id,
                'name': self.task_group1.name,
                'suggested_positions': [self.human_resource_position.title],
                'team_members': [self.regular_userprofile.email],
                'task': self.task1.id
            },
            {
                'id': self.task_group2.id,
                'name': self.task_group2.name,
                'suggested_positions': [self.human_resource_position.title],
                'team_members': [self.regular_userprofile2.email],
                'task': self.task2.id
            },
            {
                'id': self.task_group3.id,
                'name': self.task_group3.name,
                'suggested_positions': [self.human_resource_position.title],
                'team_members': [self.admin_userprofile.email],
                'task': None
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

    def test_non_task_group_members_gets_restricted_representation(self):
        """Tests if the to_representation method of the taskgroup serializer
        is preventing users from viewing tasks in which they are not a team
        member."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        queryset = models.TaskGroup.objects.all()

        serializer = TaskGroupSerializer(
            instance=queryset,
            many=True,
            context={'request': request}
        )

        representation_data = serializer.data

        expected_data = [
            None,
            None,
            {
                'id': self.task_group1.id,
                'name': self.task_group1.name,
                'suggested_positions': [self.human_resource_position.title],
                'team_members': [self.regular_userprofile.email],
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

        # Check if representation data contains all instances
        self.assertEqual(representation_data, expected_data)

    def test_slug_related_fields_working(self):
        """Tests if the taskgroup serializer is correctly setting certain fields
        to a slug field."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('taskgroup-detail', args=[self.task_group1.id])
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = TaskGroupSerializer(
            instance=self.task_group1,
            context={'request': request}
        )

        representation_data = serializer.data

        # Converting ordered_dict into regular dictionary so the different
        # order of the key value pairs within the dictionaries
        # of the representation_data and the expected_data wont throw a
        # comparison error.
        representation_data = dict(representation_data)

        expected_data = {
            'suggested_positions': [self.human_resource_position.title],
            'team_members': [self.regular_userprofile.email]
        }

        # Checks if the slugfields are occupied with the correct values
        for field in expected_data:
            self.assertEqual(representation_data[field], expected_data[field])

    # Signal handler tests
    def test_task_group_gets_created_and_assigned_to_task_when_not_yet_set(self):
        """Tests if the taskgroup is created and assigned by the signal
        handler."""

        # Connect the signal for the current test method
        post_save.connect(signals.create_task_group, sender=models.Task)

        # Task manager (Allowed to create task instances)
        self.regular_user1.profile.position.is_task_manager = True
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('task-list')
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.human_resource_category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }
        response = self.client.post(url, data, format='json')

        # Checks if a taskgroup was created by the signal handler
        task_group_id = response.data["task_group"]
        task_group_instance = models.TaskGroup.objects.get(id=task_group_id)
        self.assertIsNotNone(task_group_instance)

        # Checks if the taskgroup got assigned to the task by the signal handler
        task_id = response.data['id']
        task_instance = models.Task.objects.get(id=task_id)
        self.assertEqual(task_instance.task_group.id, task_group_instance.id)

    def test_task_group_is_not_created_and_assigned_to_task_when_already_set(self):
        """Tests if the taskgroup is not created and assigned by the signal
        handler when staff user already submitted one."""

        # Connect the signal for the current test method
        post_save.connect(signals.create_task_group, sender=models.Task)

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        # Create a task group instance
        test_task_group = models.TaskGroup.objects.create(
            name='The Test TaskGroup'
        )
        test_task_group.suggested_positions.set(
            [self.human_resource_position]
        )
        test_task_group.team_members.set([self.regular_userprofile2])

        url = reverse('task-list')
        data = {
            'owner': self.regular_user1.email,
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.human_resource_category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
            'task_group': test_task_group.id,
        }
        response = self.client.post(url, data, format='json')

        # Check if the task group set in the data is the same as in the task
        # instance retrieved from the database.
        task_id = response.data['id']
        task_instance = models.Task.objects.get(id=task_id)
        self.assertEqual(task_instance.task_group.id, test_task_group.id)

    def test_suggested_positions_get_assigned_to_task_group(self):
        """Tests if the task owner gets assigned as a team member of the
        task group, and 4 positions related with the task category get
        assigned to the suggested_positions of the task group by the signal
        handler."""

        # Connect the signal for the current test method
        post_save.connect(signals.create_task_group, sender=models.Task)

        # Task manager (Allowed to create task instances)
        self.regular_user1.profile.position.is_task_manager = True
        self.client.force_authenticate(user=self.regular_user1)

        # Creating position instances
        # Only 4 should be found in the actual data dictionary further down.
        # One of them is the self.human_resource_position created within the
        # setup. The fifth is expected to not be present in the actual data.
        human_resource_position2 = models.Position.objects.create(
            title='Human Resource Position 2',
            description='''A dummy position instance for testing purposes''',
            is_task_manager=True,
            category=self.human_resource_category,
        )
        human_resource_position3 = models.Position.objects.create(
            title='Human Resource Position 3',
            description='''A dummy position instance for testing purposes''',
            is_task_manager=True,
            category=self.human_resource_category,
        )
        human_resource_position4 = models.Position.objects.create(
            title='Human Resource Position 4',
            description='''A dummy position instance for testing purposes''',
            is_task_manager=True,
            category=self.human_resource_category,
        )
        human_resource_position5 = models.Position.objects.create(
            title='Human Resource Position 5',
            description='''A dummy position instance for testing purposes''',
            is_task_manager=True,
            category=self.human_resource_category,
        )

        # Sending a post request to create a new task instance to trigger
        # the signal handler for he creation of a task group for the task
        # instance.
        url = reverse('task-list')
        data = {
            'title': 'The first Task',
            'description': 'The task to be tested.',
            'due_date': date(2023, 1, 15),
            'category': self.human_resource_category.name,
            'priority': self.priority.caption,
            'status': self.status.caption,
        }
        response = self.client.post(url, data, format='json')

        # Retrieving the by the signal handler created and assigned
        # task group.
        task_id = response.data['id']
        task_group_instance = models.TaskGroup.objects.get(
            task=task_id
        )

        # Retrieving the positions and team members from the newly created
        # task group (by the signal handler) to create 2 lists that can
        # occupy the suggested_positions and team_members field of the actual
        # data dictionary so a comparison can be made with the expected data
        # dictionary.
        positions = []
        team_members = []
        for position in task_group_instance.suggested_positions.all():
            positions.append(position.title)
        for member in task_group_instance.team_members.all():
            team_members.append(member.email)

        # The prepared actual data to be compared
        actual_data = {
            'id': task_group_instance.id,
            'name': task_group_instance.name,
            'suggested_positions': positions,
            'team_members': team_members,
            'task': task_id
        }

        # The expected data to be compared
        expected_data = {
            'id': task_group_instance.id,
            'name': task_group_instance.name,
            'suggested_positions': [
                self.human_resource_position.title,
                human_resource_position2.title,
                human_resource_position3.title,
                human_resource_position4.title,
            ],
            'team_members': [self.regular_userprofile.email],
            'task': task_id
        }

        # Check if the suggested_positions/team_members got assigned
        # correctly.
        self.assertEqual(actual_data, expected_data)
