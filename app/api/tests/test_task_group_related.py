# from rest_framework.test import APITestCase
# from datetime import date
# from api.serializers import TaskGroupSerializer
# from django.urls import reverse
# from api.models import Priority, Status, Category, Position, UserProfile, \
#     Task, TaskGroup
# from django.contrib.auth import get_user_model
# from rest_framework import status
# from django.db.models.signals import post_save
# from api.signals import create_task_group, create_or_update_profile


# """Tests that are related to the task group model."""

# User = get_user_model()


# class TestTaskGroupModel(APITestCase):
#     """Tests that are related to the task group model."""

#     def setUp(self) -> None:
#         # Disconnect the signal during the test setup
#         post_save.disconnect(create_task_group, sender=Task)
#         post_save.disconnect(create_or_update_profile, sender=User)

#         # Creating user instance 1
#         self.user = User.objects.create(
#             email='peterpahn@gmail.com',
#             password='blabla123.'
#         )

#         # Creating user instance 2
#         self.user2 = User.objects.create(
#             email='tinaturner@gmail.com',
#             password='blabla123.'
#         )

#         # Creating user instance 3
#         self.user3 = User.objects.create(
#             email='captaincook@gmail.com',
#             password='blabla123.'
#         )

#         # Priority instance
#         caption = 'High Priority'
#         self.priority = Priority.objects.create(caption=caption)

#         # Status instance
#         caption = 'In Progress'
#         self.status = Status.objects.create(caption=caption)

#         # Category instance
#         self.category = Category.objects.create(
#             name='Human Resource Management',
#             description='Human Resource Management task category involves'
#             'overseeing recruitment, employee development, performance'
#             'evaluation, and maintaining a positive workplace culture to'
#             'optimize the organizations human capital.'
#         )

#         # Position instance
#         self.position = Position.objects.create(
#             title='Human Resource Specialist',
#             description='A Human Resource Specialist focuses on recruitment,'
#             'employee relations, benefits administration, and workforce'
#             'planning, ensuring effective management of human resources'
#             'within an organization.',
#             is_task_manager=False,
#             related_category=self.category
#         )

#         # Position instance 2
#         self.position2 = Position.objects.create(
#             title='Recruitment Specialist',
#             description='In charge of the recruitment and selection process,'
#             'including sourcing candidates, conducting interviews, and'
#             'managing the onboarding process for new employees.',
#             is_task_manager=False,
#             related_category=self.category
#         )

#         # Position instance 3
#         self.position3 = Position.objects.create(
#             title='Training and Development Specialist',
#             description='Focuses on employee training and development'
#             'programs, assessing training needs, designing and delivering'
#             'training sessions, and supporting employees in enhancing'
#             'their skills.',
#             is_task_manager=False,
#             related_category=self.category
#         )

#         # Position instance 4
#         self.position4 = Position.objects.create(
#             title='Compensation and Benefits Specialist',
#             description='Manages the companys compensation and benefits'
#             'programs, including salary structures, incentive programs,'
#             'health insurance, and other employee benefits.',
#             is_task_manager=False,
#             related_category=self.category
#         )

#         # Position instance 5
#         self.position5 = Position.objects.create(
#             title='Employee Relations Specialist',
#             description='Handles employee relations matters, including'
#             'conflict resolution, employee grievances, and ensuring a'
#             'positive and productive work environment. This role may also'
#             'involve conducting investigations into employee complaints and'
#             'implementing strategies to improve employee engagement.',
#             is_task_manager=False,
#             related_category=self.category
#         )

#         # Creating userprofile instance 1
#         self.userprofile = UserProfile.objects.create(
#             owner=self.user,
#             first_name='Peter',
#             last_name='Pahn',
#             phone_number=int('0163557799'),
#             email=self.user.email,
#             position=self.position
#         )

#         # Creating userprofile instance 2
#         self.userprofile2 = UserProfile.objects.create(
#             owner=self.user2,
#             first_name='Tina',
#             last_name='Turner',
#             phone_number=int('0176559934'),
#             email=self.user2.email,
#             position=self.position
#         )

#         # Creating userprofile instance 3
#         self.userprofile3 = UserProfile.objects.create(
#             owner=self.user3,
#             first_name='Captain',
#             last_name='Cook',
#             phone_number=int('0176577922'),
#             email=self.user3.email,
#             position=self.position
#         )

#         # Craeting a taskgroup instance
#         self.task_group = TaskGroup.objects.create(
#             name='The first TaskGroup'
#         )
#         self.task_group.suggested_positions.set([self.position])
#         self.task_group.team_members.set([self.userprofile])

#         # Craeting a taskgroup instance 3
#         self.task_group3 = TaskGroup.objects.create(
#             name='The second TaskGroup'
#         )
#         self.task_group3.suggested_positions.set([self.position])
#         self.task_group3.team_members.set([self.userprofile3])

#         # Creating a task instance and assigning it to user
#         self.task = Task.objects.create(
#             title='The first Task',
#             description='The task to be tested.',
#             due_date=date(2023, 1, 15),
#             category=self.category,
#             priority=self.priority,
#             status=self.status,
#             owner=self.userprofile,
#             task_group=self.task_group
#         )

#         # Creating a task instance and assigning it to user3
#         self.task3 = Task.objects.create(
#             title='The second Task',
#             description='The second task to be tested.',
#             due_date=date(2023, 1, 16),
#             category=self.category,
#             priority=self.priority,
#             status=self.status,
#             owner=self.userprofile3,
#             task_group=self.task_group3
#         )

#     # List view
#     def test_authenticated_user_can_access_list(self):
#         """Tests if the list view action allows authenticated users."""

#         self.client.force_authenticate(user=self.user)
#         url = reverse('taskgroup-list')

#         response = self.client.get(url, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_unauthenticated_user_cant_access_list(self):
#         """Tests if the list view action disallows unauthenticated users."""

#         url = reverse('taskgroup-list')
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Retrieve
#     def test_authenticated_user_can_access_retrieve(self):
#         """Tests if the retrieve view action disallows unauthenticated
#         users."""

#         self.client.force_authenticate(user=self.user)
#         url = reverse('taskgroup-detail', args=[self.task.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_unauthenticated_user_cant_access_retrieve(self):
#         """Tests if the retrieve view action disallows unauthenticated
#         users."""

#         url = reverse('taskgroup-detail', args=[self.task.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Create view
#     def test_staff_can_access_create(self):
#         """Tests if the create view action allows staff users."""

#         self.client.force_authenticate(user=self.user)
#         self.user.is_staff = True

#         new_task = Task.objects.create(
#             title='The new Task',
#             description='The new task to be tested.',
#             due_date=date(2023, 1, 20),
#             category=self.category,
#             priority=self.priority,
#             status=self.status,
#             owner=self.userprofile,
#         )
#         url = reverse('taskgroup-list')
#         data = {
#             'name': 'The first TaskGroup',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': new_task.id
#         }

#         response = self.client.post(url, data, format='json')

#         # Check if the task was created
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_non_staff_cant_access_create(self):
#         """Tests if the create view action diallows non staff users."""

#         self.user.is_staff = False
#         self.client.force_authenticate(user=self.user)

#         new_task = Task.objects.create(
#             title='The new Task',
#             description='The new task to be tested.',
#             due_date=date(2023, 1, 20),
#             category=self.category,
#             priority=self.priority,
#             status=self.status,
#             owner=self.userprofile,
#         )
#         url = reverse('taskgroup-list')
#         data = {
#             'name': 'The first TaskGroup',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': new_task.id
#         }

#         response = self.client.post(url, data, format='json')
#         print(response.content)

#         # Check if the permission is denied for non staff users
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_unauthenticated_cant_access_create(self):
#         """Tests if the create view action diallows unauthenticated users."""

#         self.user.is_staff = True

#         new_task = Task.objects.create(
#             title='The new Task',
#             description='The new task to be tested.',
#             due_date=date(2023, 1, 20),
#             category=self.category,
#             priority=self.priority,
#             status=self.status,
#             owner=self.userprofile,
#         )
#         url = reverse('taskgroup-list')
#         data = {
#             'name': 'The first TaskGroup',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': new_task.id
#         }

#         response = self.client.post(url, data, format='json')
#         print(response.content)

#         # Check if the permission is denied for aunauthenticated users
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Destroy view
#     def test_staff_can_access_destroy(self):
#         """Tests if the destroy view action allows staff users."""

#         self.user2.is_staff = True
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_non_staff_cant_access_destroy(self):
#         """Tests if the destroy view action disallows non staff users."""

#         self.user2.is_staff = False
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_unauthenticated_cant_access_destroy(self):
#         """Tests if the destroy view action disallows unauthenticated
#         users."""

#         self.user2.is_staff = True

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Update view
#     def test_staff_can_access_update(self):
#         """Tests if the update view action allows staff
#         users."""

#         self.user2.is_staff = True
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Updated task group',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': self.task.id
#         }

#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_non_staff_cant_access_update(self):
#         """Tests if the update view action allows staff
#         users."""

#         self.user2.is_staff = False
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Updated task group',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': self.task.id
#         }

#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_owner_can_access_update(self):
#         """Tests if the update view action allows owner."""

#         self.client.force_authenticate(user=self.user)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Updated task group',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': self.task.id
#         }

#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_non_owner_cant_access_update(self):
#         """Tests if the update view action disallows non owner."""

#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Updated task group',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': self.task.id
#         }

#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_unauthenticated_cant_access_update(self):
#         """Tests if the update view action disallows unauthenticated
#         users."""

#         self.user2.is_staff = True

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Updated task group',
#             'suggested_positions': [self.position.title],
#             'team_members': [self.userprofile.email],
#             'assigned_task': self.task.id
#         }

#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Partial update view
#     def test_staff_can_access_partial_update(self):
#         """Tests if the partial update view action allows staff
#         users."""

#         self.user2.is_staff = True
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Partially updated task group',
#             'suggested_positions': [self.position.title],
#         }

#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_non_staff_cant_access_partial_update(self):
#         """Tests if the partial update view action disallows non staff
#         users."""

#         self.user2.is_staff = False
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Partially updated task group',
#             'suggested_positions': [self.position.title],
#         }

#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_owner_can_access_partial_update(self):
#         """Tests if the partial update view action allows owner."""

#         self.client.force_authenticate(user=self.user)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Partially updated task group',
#             'suggested_positions': [self.position.title],
#         }

#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_non_owner_cant_access_partial_update(self):
#         """Tests if the partial update view action disallows owner."""

#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Partially updated task group',
#             'suggested_positions': [self.position.title],
#         }

#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_unauthenticated_cant_access_partial_update(self):
#         """Tests if the partial update view action disallows staff
#         users."""

#         self.user2.is_staff = True

#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         data = {
#             'name': 'Partially updated task group',
#             'suggested_positions': [self.position.title],
#         }

#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # Serializer
#     def test_fields_read_only_staff_user(self):
#         """Tests if the get_fields method of the taskserializer is setting
#         only the id field to read-only for staff users."""

#         self.user2.is_staff = True
#         self.client.force_authenticate(user=self.user2)
#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         response = self.client.get(url, format='json')
#         request = response.wsgi_request

#         serializer = TaskGroupSerializer(
#             instance=self.task_group,
#             context={'request': request}
#         )

#         fields = serializer.fields
#         # ID field is read only by default
#         fields.pop('id', None)

#         # Checks if all other fields are modifiable
#         for field, field_instance in fields.items():
#             self.assertFalse(field_instance.read_only)

#     def test_owner_fields_read_only(self):
#         """Tests if the get_fields method of the taskserializer is setting
#         certain fields to read-only for for the owner."""

#         self.client.force_authenticate(user=self.user)
#         url = reverse('taskgroup-detail', args=[self.task_group.id])

#         response = self.client.get(url, format='json')
#         request = response.wsgi_request

#         serializer = TaskGroupSerializer(
#             instance=self.task_group,
#             context={'request': request}
#         )

#         fields = serializer.fields
#         read_only_fields = ['id', 'assigned_task']

#         for field, field_instance in fields.items():
#             # Checks if all fields expected to be read only true are correct
#             if field in read_only_fields:
#                 self.assertTrue(field_instance.read_only)

#             # Checks if all fields expected to be read only false are correct
#             else:
#                 self.assertFalse(field_instance.read_only)

#     def test_staff_gets_unrestricted_representation(self):
#         """Tests if the to_representation method of the taskgroupserializer is
#         granting full representation to each task."""

#         # Staff users can see every instance
#         self.user2.is_staff = True
#         self.client.force_authenticate(user=self.user2)

#         url = reverse('taskgroup-list')
#         response = self.client.get(url, format='json')
#         request = response.wsgi_request

#         queryset = TaskGroup.objects.all()

#         serializer = TaskGroupSerializer(
#             instance=queryset,
#             many=True,
#             context={'request': request}
#         )

#         representation_data = serializer.data
#         representation_data_list = [dict(item) for item in representation_data]

#         expected_data = [
#             {
#                 'id': self.task_group.id,
#                 'name': 'The first TaskGroup',
#                 'suggested_positions': ['Human Resource Specialist'],
#                 'team_members': ['peterpahn@gmail.com'],
#                 'assigned_task': self.task.id
#             },
#             {
#                 'id': self.task_group3.id,
#                 'name': 'The second TaskGroup',
#                 'suggested_positions': ['Human Resource Specialist'],
#                 'team_members': ['captaincook@gmail.com'],
#                 'assigned_task': self.task3.id
#             }
#         ]
#         self.assertEqual(representation_data_list, expected_data)

#     def test_non_task_members_gets_restricted_representation(self):
#         """Tests if the to_representation method of the taskgroup serializer
#         is preventing users from viewing tasks in which they are not a team
#         member."""

#         self.client.force_authenticate(user=self.user3)

#         url = reverse('taskgroup-list')
#         response = self.client.get(url, format='json')
#         request = response.wsgi_request

#         queryset = TaskGroup.objects.all()

#         serializer = TaskGroupSerializer(
#             instance=queryset,
#             many=True,
#             context={'request': request}
#         )

#         representation_data = serializer.data
#         representation_data_list = [dict(item) for item in representation_data]

#         expected_data = [
#             {},
#             {
#                 'id': self.task_group3.id,
#                 'name': 'The second TaskGroup',
#                 'suggested_positions': ['Human Resource Specialist'],
#                 'team_members': ['captaincook@gmail.com'],
#                 'assigned_task': self.task3.id
#             }
#         ]
#         self.assertEqual(representation_data_list, expected_data)

#     def test_slug_related_fields_working(self):
#         """Tests if the taskgroup serializer is correctly setting certain fields
#         to a slug field."""

#         self.client.force_authenticate(user=self.user)
#         url = reverse('taskgroup-detail', args=[self.task_group.id])
#         response = self.client.get(url, format='json')
#         request = response.wsgi_request

#         serializer = TaskGroupSerializer(
#             instance=self.task_group,
#             context={'request': request}
#         )

#         representation_data = serializer.data
#         expected_data = {
#             'suggested_positions': ['Human Resource Specialist'],
#             'team_members': ['peterpahn@gmail.com']
#         }

#         # Checks if the slugfields are occupied with the correct values
#         for field in expected_data:
#             self.assertEqual(representation_data[field], expected_data[field])

#     # Signal handler tests
#     def test_task_group_gets_created_and_assigned_to_task(self):
#         """Tests if the taskgroup is created and assigned by the signal
#         handler."""

#         # Connect the signal for the current test method
#         post_save.connect(create_task_group, sender=Task)

#         self.user2.profile.position.is_task_manager = True
#         self.client.force_authenticate(user=self.user2)
#         url = reverse('task-list')
#         data = {
#             'title': 'The first Task',
#             'description': 'The task to be tested.',
#             'due_date': date(2023, 1, 15),
#             'category': self.category.name,
#             'priority': self.priority.caption,
#             'status': self.status.caption,
#         }

#         response = self.client.post(url, data, format='json')

#         # Checks if a taskgroup was created by the signal handler
#         task_group_id = response.data["task_group"]
#         task_group = TaskGroup.objects.get(id=task_group_id)
#         self.assertIsNotNone(task_group)

#         # Checks if the taskgroup got assigned to the task by the signal handler
#         task_id = response.data['id']
#         task = Task.objects.get(id=task_id)
#         self.assertEqual(task.task_group.id, task_group.id)

#     def test_suggested_positions_get_assigned_to_task_group(self):
#         """Tests if the suggested positions and team members are getting
#         assigned o the task group by the signal handler."""

#         # Connect the signal for the current test method
#         post_save.connect(create_task_group, sender=Task)

#         self.client.force_authenticate(user=self.user2)
#         self.user2.profile.position.is_task_manager = True
#         url = reverse('task-list')
#         data = {
#             'title': 'The first Task',
#             'description': 'The task to be tested.',
#             'due_date': date(2023, 1, 15),
#             'category': self.category.name,
#             'priority': self.priority.caption,
#             'status': self.status.caption,
#         }

#         response = self.client.post(url, data, format='json')

#         task_id = response.data['id']
#         task_group = TaskGroup.objects.get(assigned_task=task_id)

#         positions = []
#         members = []

#         for position in task_group.suggested_positions.all():
#             positions.append(position.title)

#         for member in task_group.team_members.all():
#             members.append(member.email)

#         actual_data = {
#             'id': task_group.id,
#             'name': task_group.name,
#             'suggested_positions': positions,
#             'team_members': members,
#             'assigned_task': task_id
#         }

#         expected_data = {
#             'id': task_group.id,
#             # 'TaskGroup of' gets added by the signal handler
#             'name': 'TaskGroup of The first Task',
#             'suggested_positions': [
#                 self.position.title,
#                 self.position2.title,
#                 self.position3.title,
#                 self.position4.title,
#                 self.position5.title
#             ],
#             'team_members': [self.userprofile2.email],
#             'assigned_task': task_id
#         }

#         self.assertEqual(actual_data, expected_data)
