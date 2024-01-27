from rest_framework.test import APITestCase
from api import models, serializers, signals
from rest_framework import status
from django.urls import reverse
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCustomUserModel(APITestCase):
    """Tests that are related to the CustomUser model."""

    def setUp(self) -> None:
        '''The creation of the following instances are necessary to test the
        category view nd eventual serializer, signal handler etc.'''

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
            related_category=self.human_resource_category
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

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('customuser-list')
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        # Unauthenticated user

        url = reverse('customuser-list')
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'customuser-detail',
            args=[self.regular_user1.id]
        )
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse(
            'customuser-detail',
            args=[self.regular_user1.id]
        )
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_unauthenticated_user_can_access_create(self):
        """Tests if the create view action allows unauthenticated users."""

        # unauthenticated user

        url = reverse('customuser-list')
        data = {
            'email': 'alibaba@gmail.com',
            'password': 'blabla123.'
        }
        response = self.client.post(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('customuser-detail', args=[self.regular_user1.id])
        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_access_update(self):
        """Tests if the update view action allows owner."""

        # Object owner
        self.client.force_authenticate(user=self.regular_user2)

        url = reverse('customuser-detail', args=[self.regular_user2.id])
        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_and_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non owner and non staff
        users."""

        # Non-staff user who's also not the object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('customuser-detail', args=[self.regular_user2.id])
        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated
        users."""

        # Unauthenticted user

        url = reverse('customuser-detail', args=[self.regular_user1.id])
        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',
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

        url = reverse('customuser-detail', args=[self.regular_user1.id])
        data = {
            'email': 'different@gmail.com'
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_access_partial_update(self):
        """Tests if the partial update view action allows owner."""

        # Object owner
        self.client.force_authenticate(user=self.regular_user2)

        url = reverse('customuser-detail', args=[self.regular_user2.id])
        data = {
            'email': 'different@gmail.com'
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_and_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non owner and
        non staff users."""

        # Non-staff user who's also not the object owner
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('customuser-detail', args=[self.regular_user2.id])
        data = {
            'email': 'different@gmail.com'
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial update view action disallows unauthenticated
        users."""

        # Unauthenticated user

        url = reverse('customuser-detail', args=[self.regular_user1.id])
        data = {
            'email': 'different@gmail.com'
        }
        response = self.client.patch(url, data, format='json')

        # Check if access was denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('customuser-detail', args=[self.regular_user1.id])
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('customuser-detail', args=[self.regular_user2.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_destroy(self):
        """Tests if the destroy view action disallows non owner."""

        # Unauthenticated user

        url = reverse('customuser-detail', args=[self.regular_user1.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializer
    def test_staff_user_serializer_fields_read_only(self):
        """Tests if the get fields method of the serializer is keeping each
        field writable for staff users (exept id field)."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('customuser-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.regular_user1,
            context={'request': request}
        )
        fields = serializer.fields

        # List of expected read-only fields
        read_only_fields = ['id']

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

        url = reverse('customuser-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.regular_user1,
            context={'request': request}
        )
        fields = serializer.fields

        # List of expected read-only fields
        read_only_fields = ['id', 'profile']

        # Check if fields are set to read-only correctly
        for field, field_instance in fields.items():
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)

            else:
                self.assertFalse(field_instance.read_only)

    def test_serializer_password_field(self):
        """Tests if the get fields method of the serializer is setting
        the password field to write only and setting the input style to
        password."""

        # No need for specific user permissions
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('customuser-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.regular_user1,
            context={'request': request}
        )
        password_field = serializer.fields['password']

        # Check if password field is set to read-only
        self.assertTrue(password_field.write_only)

        # Checks if input style is password
        pw_input_style = password_field.style.get('input_style', None)
        self.assertEqual(pw_input_style, 'password')

    def test_serializer_profile_field(self):
        """Tests if the get fields method of the serializer is setting
        the profile field to required false."""

        # No need for specific user permissions
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('customuser-list')
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.regular_user1,
            context={'request': request}
        )
        profile_field = serializer.fields['profile']

        # Checks if profile field is not required
        self.assertFalse(profile_field.required)
