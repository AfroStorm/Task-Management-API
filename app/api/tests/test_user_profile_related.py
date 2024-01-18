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

        # Disconnect the signal during the test setup
        post_save.disconnect(signals.create_task_group, sender=models.Task)
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
        url = reverse('userprofile-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        url = reverse('userprofile-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('userprofile-detail', args=[self.userprofile.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        url = reverse('userprofile-detail', args=[self.userprofile.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_user_can_access_create(self):
        """Tests if the create view action allows staff users."""

        self.client.force_authenticate(user=self.user2)
        self.user2.is_staff = True
        url = reverse('userprofile-list')
        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.post(url, data, format='json')

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_user_cant_access_create(self):
        """Tests if the create view action allows staff users."""

        self.client.force_authenticate(user=self.user2)
        url = reverse('userprofile-list')
        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.post(url, data, format='json')

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_update(self):
        """Tests if the update view action allows owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_update(self):
        """Tests if the update view action disallows non owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_update(self):
        """Tests if the update view action disallows unauthenticated
        users."""

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'first_name': 'Sebastian',
            'last_name': 'Schuhmacher',
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff users."""

        self.user2.is_staff = False
        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_access_partial_update(self):
        """Tests if the partial update view action allows owner."""

        self.client.force_authenticate(user=self.user)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non owner."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cant_access_partial_update(self):
        """Tests if the partial update view action disallows unauthenticated
        users."""

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        data = {
            'owner': self.user3.email,
            'phone_number': '0176554488',
            'email': 's.schuhmacher@gmil.com',
            'position': self.position.id
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cant_access_destroy(self):
        """Tests if the destroy view action disallows non owner."""

        url = reverse('userprofile-detail', args=[self.userprofile.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Serializers
    def test_serializer_fields_read_only_staff_user(self):
        """Tests if the get fields method of the serializer is keeping each
        field writable for staff users (exept id field)."""

        self.user2.is_staff = True

        url = reverse('userprofile-list')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.UserProfileSerializer(
            instance=self.userprofile,
            context={'request': request}
        )

        fields = serializer.fields
        fields.pop('id', None)

        for field, field_instance in fields.items():
            self.assertFalse(field_instance.read_only)

    def test_serializer_fields_read_only_non_staff_user(self):
        """Tests if the get fields method of the serializer is setting
        certain fields to read only for non staff users."""

        url = reverse('userprofile-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        request = response.wsgi_request

        serializer = serializers.TaskSerializer(
            instance=self.userprofile,
            context={'request': request}
        )

        fields = serializer.fields
        read_only_fields = ['id', 'owner', 'task_group', 'tasks_to_manage']

        for field, field_instance in fields.items():
            # Checks if all fields expected to be read only true are correct
            if field in read_only_fields:
                self.assertTrue(field_instance.read_only)
            # Checks if all fields expected to be read only false are correct
            else:
                self.assertFalse(field_instance.read_only)

    # Signal handler
    def test_user_profile_gets_created_and_assigned_when_not_yet_set(self):
        """Tests if the userprofile is created and assigned by the signal
        handler."""

        post_save.connect(signals.create_or_update_profile, sender=User)

        url = reverse('customuser-list')
        data = {
            'email': 'alibaba@gmail.com',
            'password': 'blabla123.',
        }

        response = self.client.post(url, data, format='json')

        # Checks if instance waas created
        profile_id = response.data['profile']
        profile_instance = models.UserProfile.objects.get(id=profile_id)
        self.assertIsNotNone(profile_instance)

        # Checks if profile was assigned correctly
        user_id = response.data['id']
        user_instance = User.objects.get(id=user_id)
        self.assertEqual(user_instance, profile_instance.owner)

    # def test_user_profile_is_no_created_and_assigned_when_already_set(self):
    #     """Tests if the userprofile doesnt get created and assigned by the
    #     signal handler if its already set by the staff user."""

    #     post_save.connect(signals.create_or_update_profile, sender=User)
    #     self.user2.is_staff = True
    #     self.client.force_authenticate(user=self.user2)
    #     url = reverse('customuser-list')

    #     data = {
    #         'email': 'alibaba@gmail.com',
    #         'password': 'blabla123.',
    #         'profile': 'blabla123.',
    #     }

    #     response = self.client.post(url, data, format='json')

    #     # Checks if instance waas created
    #     profile_id = response.data['profile']
    #     profile_instance = models.UserProfile.objects.get(id=profile_id)
    #     self.assertIsNotNone(profile_instance)

    #     # Checks if profile was assigned correctly
    #     user_id = response.data['id']
    #     user_instance = User.objects.get(id=user_id)
    #     self.assertEqual(user_instance, profile_instance.owner)

    # def test_user_profile_email_gets_assigned(self):
    #     """Tests if the userprofile email field gets assigned by the signal
    #     handler."""

    #     post_save.connect(signals.create_or_update_profile, sender=User)

    #     url = reverse('customuser-list')
    #     data = {
    #         'email': 'alibaba@gmail.com',
    #         'password': 'blabla123.',
    #     }

    #     response = self.client.post(url, data, format='json')

    #     # Checks if the profile email is the same as the user email
    #     user_email = response.data['email']
    #     profile_instnce = models.UserProfile.objects.get(email=user_email)
    #     self.assertEqual(profile_instnce.email, user_email)
