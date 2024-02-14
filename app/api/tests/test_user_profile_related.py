from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models.signals import post_save
from rest_framework import status
from api import models, signals, serializers


User = get_user_model()


class TestUserProfileModel(APITestCase):
    """Tests that are related to the UserProfile model."""

    def setUp(self) -> None:
        '''The creation of the following instances are necessary to test the
        user view nd eventual serializer, signal handler etc.'''

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
            first_name='Chris',
            last_name='Tucker',
            phone_number=int('0176339934'),
            email=self.regular_user2.email,
            position=self.human_resource_position
        )

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('userprofile-list')
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        # Unauthenticated user

        url = reverse('userprofile-list')
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse(
            'userprofile-detail',
            args=[self.regular_user1.id]
        )
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_user_can_access_create(self):
        """Tests if the create view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('userprofile-list')
        data = {
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.post(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_user_cant_access_create(self):
        """Tests if the create view action allows staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('userprofile-list')
        data = {
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.post(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_create(self):
        """Tests if the create view action allows unauthenticated users."""

        # Unauthenticated user

        url = reverse('userprofile-list')
        data = {
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.post(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff
        users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        data = {
            'owner': self.regular_user1.id,
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '0176554488',
            'email': 'updatedemail@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_access_update(self):
        """Tests if the update view action allows owner."""

        # Object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        data = {
            'owner': self.regular_user1.email,
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '0176554488',
            'email': 'updatedemail@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_and_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non owner and non staff
        users."""

        # Non-staff user who's also not the object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile2.id]
        )
        data = {
            'owner': self.regular_user2.email,
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '0176554488',
            'email': 'updatedemail@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated
        users."""

        # Unauthenticated user

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile2.id]
        )
        data = {
            'owner': self.regular_user2.email,
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '0176554488',
            'email': 'updatedemail@gmail.com',
            'position': self.human_resource_position.title
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_access_partial_update(self):
        """Tests if the partial update view action allows owner."""

        # Object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_and_non_owner_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non owner and
        non staff users."""

        # Non-staff user who's also not the object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile2.id]
        )
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial update view action disallows unauthenticated
        users."""

        # Unauthenticated user

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile2.id]
        )
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        # Saff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_destroy(self):
        """Tests if the destroy view action disallows non owner."""

        # Unauthenticated user

        url = reverse(
            'userprofile-detail',
            args=[self.regular_userprofile.id]
        )
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializers
    def test_staff_user_serializer_fields_read_only(self):
        """Tests if the get fields method of the serializer is keeping each
        field writable for staff users (exept id field)."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('userprofile-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.UserProfileSerializer(
            instance=self.regular_userprofile,
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

    def test_non_staff_user_serializer_fields_read_only(self):
        """Tests if the get fields method of the serializer is setting
        certain fields to read only for non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('userprofile-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.UserProfileSerializer(
            instance=self.regular_userprofile,
            context={'request': request}
        )

        fields = serializer.fields

        # List of expected read-only fields
        read_only_fields = [
            'id', 'owner', 'taskgroup_set', 'task_set', 'position'
        ]

        # Check if fields are set to read-only correctly
        for field, field_instance in fields.items():
            if field in read_only_fields:
                print(f'READ ONLY FIELD: {field}')
                self.assertTrue(field_instance.read_only)

            else:
                print(f'WRITABLE FIELD: {field}')
                self.assertFalse(field_instance.read_only)

    # Signal handler
    def test_user_profile_gets_created_and_assigned_when_not_yet_set(self):
        """Tests if the userprofile is created and assigned by the signal
        handler after a new user was created."""

        # Activate signal handler for creating
        post_save.connect(signals.create_or_update_profile, sender=User)

        url = reverse('customuser-list')
        data = {
            'email': 'alibaba@gmail.com',
            'password': 'blabla123.',
        }
        response = self.client.post(url, data, format='json')

        # Checks if instance was created
        profile_id = response.data['profile']
        profile_instance = models.UserProfile.objects.get(id=profile_id)
        self.assertIsNotNone(profile_instance)

        # Checks if profile was assigned correctly
        user_id = response.data['id']
        user_instance = User.objects.get(id=user_id)
        self.assertEqual(user_instance.profile, profile_instance)

    def test_user_profile_email_gets_assigned(self):
        """Tests if the userprofile email field gets assigned by the signal
        handler based on the newly created user's email."""

        # Activate signal handler for creating
        post_save.connect(signals.create_or_update_profile, sender=User)

        # Unauthenticated user so the userprofile gets created by the
        # signal handler

        url = reverse('customuser-list')
        data = {
            'email': 'alibaba@gmail.com',
            'password': 'blabla123.',
        }
        response = self.client.post(url, data, format='json')

        # Checks if profile email was assigned correctly
        email_id = response.data['email']
        profile_instance = models.UserProfile.objects.get(email=email_id)
        user_id = response.data['id']
        user_instance = User.objects.get(id=user_id)
        self.assertEqual(profile_instance.email, user_instance.email)

    def test_user_profile_gets_not_created_and_assigned_when_already_set(self):
        """Tests if the userprofile doesnt get created and assigned to the
        user by the signal handler after a new user was created if its
        already set by the staff user."""

        # Activate signal handler for creating
        post_save.connect(signals.create_or_update_profile, sender=User)

        # Using staff user to have writing rights to all fields when creating
        # a user, so the owner field can be set
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('customuser-list')
        one_off_userprofile = models.UserProfile.objects.create(
            first_name='Sebastian',
            last_name='Schuhmacher',
            phone_number='0176554488',
            position=self.human_resource_position
        )

        # Creating user instance
        data = {
            'email': 'alibaba@gmail.com',
            'password': 'blabla123.',
            'profile': one_off_userprofile.id
        }
        response = self.client.post(url, data, format='json')

        # Checks if profile was assigned correctly
        profile_id = response.data['profile']
        profile_instance = models.UserProfile.objects.get(id=profile_id)
        self.assertEqual(one_off_userprofile, profile_instance)
