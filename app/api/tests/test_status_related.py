from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from api import models, signals
from django.db.models.signals import post_save


User = get_user_model()


class TestStatusModel(APITestCase):
    """Tests that are related to the Status model."""

    def setUp(self) -> None:
        '''The creation of the following instances are necessary to test the
        status view nd eventual serializer, signal handler etc.'''

        # Deactivate signal handlers for more control over setUp instances
        post_save.disconnect(signals.create_or_update_profile, sender=User)
        post_save.disconnect(signals.create_task_group, sender=models.Task)

        # Creating user instances
        self.regular_user1 = User.objects.create(
            email='peterpahn@gmail.com',
            password='blabla123.'
        )
        self.admin_user = User.objects.create(
            email='tinaturner@gmail.com',
            password='blabla123.',
            is_staff=True
        )

        # Creating status instances
        self.in_progress_status = models.Status.objects.create(
            caption='Task In Progress'
        )
        self.concluded_status = models.Status.objects.create(
            caption='Task Concluded'
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

        url = reverse('status-list')
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        # Unauthenticated user

        url = reverse('status-list')
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        # Authenticated user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse(
            'status-detail',
            args=[self.in_progress_status.id]
        )
        response = self.client.get(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        # Unauthenticated user

        url = reverse(
            'status-detail',
            args=[self.in_progress_status.id]
        )
        response = self.client.get(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_can_access_create(self):
        """Tests if the create view action allows staff users."""

        # Staff user
        self.regular_user1.is_staff = True
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('status-list')
        data = {
            'caption': 'Recently Opened'
        }
        response = self.client.post(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_cant_access_create(self):
        """Tests if the create view action diallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('status-list')
        data = {
            'caption': 'Recently Opened'
        }
        response = self.client.post(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('status-detail', args=[self.in_progress_status.id])
        data = {
            'caption': 'Task Concluded'
        }
        response = self.client.put(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('status-detail', args=[self.in_progress_status.id])
        data = {
            'caption': 'Task Concluded'
        }
        response = self.client.put(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        # Staff user
        self.admin_user.is_staff = True
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('status-detail', args=[self.in_progress_status.id])
        data = {
            'caption': 'Task Concluded'
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff
        users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('status-detail', args=[self.in_progress_status.id])
        data = {
            'caption': 'Task Concluded'
        }
        response = self.client.patch(url, data, format='json')

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        # Staff user
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('status-detail', args=[self.concluded_status.id])
        response = self.client.delete(url)

        # Check if access is granted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        # Non-staff user
        self.client.force_authenticate(user=self.regular_user1)

        url = reverse('status-detail', args=[self.concluded_status.id])
        response = self.client.delete(url)

        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
