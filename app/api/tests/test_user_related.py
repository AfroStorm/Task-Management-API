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

        post_save.disconnect(signals.create_or_update_profile, sender=User)

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

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('customuser-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        url = reverse('customuser-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('customuser-detail', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        url = reverse('customuser-detail', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_user_can_access_create(self):
        """Tests if the create view action allows staff users."""

        url = reverse('customuser-list')
        data = {
            'email': 'alibaba@gmail.com',
            'password': 'blabla123.'
        }

        response = self.client.post(url, data, format='json')

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',

        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',

        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_update(self):
        """Tests if the update view action allows owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',

        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_update(self):
        """Tests if the update view action disallows non owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',

        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated
        users."""

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com',
            'password': 'jaja123.',

        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_partial_update(self):
        """Tests if the partial update view action allows owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial update view action disallows unauthenticated
        users."""

        url = reverse('customuser-detail', args=[self.user.id])

        data = {
            'email': 'different@gmail.com'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('customuser-detail', args=[self.user.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_destroy(self):
        """Tests if the destroy view action disallows non owner."""

        url = reverse('customuser-detail', args=[self.user.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializer
    def test_serializer_fields_read_only_staff_user(self):
        """Tests if the get fields method of the serializer is keeping each
        field writable for staff users (exept id field)."""

        self.user2.is_staff = True

        url = reverse('customuser-list')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.user,
            context={'request': request}
        )

        fields = serializer.fields
        read_only_fields = ['id']

        for field, field_instance in fields.items():
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)

            else:
                self.assertFalse(field_instance.read_only)

    def test_serializer_fields_read_only_non_staff_user(self):
        """Tests if the get fields method of the serializer is setting
        certain fields to read only for non staff users."""

        url = reverse('customuser-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.user,
            context={'request': request}
        )

        fields = serializer.fields
        read_only_fields = ['id', 'profile']

        for field, field_instance in fields.items():
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)

            else:
                self.assertFalse(field_instance.read_only)

    def test_serializer_password_field(self):
        """Tests if the get fields method of the serializer is setting
        the password field to write only and setting the input style to
        password."""

        url = reverse('customuser-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.user,
            context={'request': request}
        )

        password_field = serializer.fields['password']

        # Checks if password field is write only
        self.assertTrue(password_field.write_only)
        # Checks if input style is password
        pw_input_style = password_field.style.get('input_style', None)
        self.assertEqual(pw_input_style, 'password')

    def test_serializer_profile_field(self):
        """Tests if the get fields method of the serializer is setting
        the profile field to required false."""

        url = reverse('customuser-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.CustomUserSerializer(
            instance=self.user,
            context={'request': request}
        )

        profile_field = serializer.fields['profile']

        # Checks if profile field is required false
        self.assertTrue(profile_field.read_only)
