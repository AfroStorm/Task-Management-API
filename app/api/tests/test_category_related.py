from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from api import models, signals
from django.db.models.signals import post_save


User = get_user_model()


class TestCategoryModel(APITestCase):
    """Tests that are related to the Category model."""

    def setUp(self) -> None:
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

        # Category instance
        self.human_resource_category = models.Category.objects.create(
            name='Human Resource Management',
            description='Human Resource Management task category involves'
            'overseeing recruitment, employee development, performance'
            'evaluation, and maintaining a positive workplace culture to'
            'optimize the organizations human capital.'
        )

        self.financial_category = models.Category.objects.create(
            name='Financial Analysis',
            description='Financial Analysis category involves assessing the '
            'financial health of the organization by analyzing '
            'financial statements, budgeting, forecasting, and '
            'providing insights for strategic decision-making.'

        )
        self.marketing_category = models.Category.objects.create(
            name='Marketing',
            description='Marketing category involves creating, communicating'
            ', delivering, and exchanging offerings that have value for '
            'customers. It includes activities such as market research,'
            'advertising, and brand management.'

        )

        # Position instance
        self.human_resource_position = models.Position.objects.create(
            title='Human Resource Specialist',
            description='A Human Resource Specialist focuses on recruitment,'
            'employee relations, benefits administration, and workforce'
            'planning, ensuring effective management of human resources'
            'within an organization.',
            is_task_manager=False,
            related_category=self.human_resource_category
        )

        self.financial_position = models.Position.objects.create(
            title='Financial Analyst',
            description='A Financial Analyst specializes in financial planning,'
            'budgeting, and analysis. They assess financial data, prepare'
            'reports, and provide recommendations to support strategic'
            'financial decision-making within the organization.',
            is_task_manager=False,
            related_category=self.financial_category
        )

        # Creating userprofile instance 1
        self.userprofile = models.UserProfile.objects.create(
            owner=self.user,
            first_name='Peter',
            last_name='Pahn',
            phone_number=int('0163557799'),
            email=self.user.email,
            position=self.human_resource_position
        )

        # Creating userprofile instance 2
        self.userprofile2 = models.UserProfile.objects.create(
            owner=self.user2,
            first_name='Tina',
            last_name='Turner',
            phone_number=int('0176559934'),
            email=self.user2.email,
            position=self.financial_position
        )

    # List view
    def test_authenticated_user_can_access_list(self):
        """Tests if the list view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_list(self):
        """Tests if the list view action disallows unauthenticated users."""

        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve view
    def test_authenticated_user_can_access_retrieve(self):
        """Tests if the retrieve view action allows authenticated users."""

        self.client.force_authenticate(user=self.user)
        url = reverse('category-detail',
                      args=[self.human_resource_category.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cant_access_retrieve(self):
        """Tests if the retrieve view action disallows unauthenticated users.
        """

        url = reverse('category-detail',
                      args=[self.human_resource_category.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Create view
    def test_staff_can_access_create(self):
        """Tests if the create view action allows staff users."""

        self.user.is_staff = True
        self.client.force_authenticate(user=self.user)

        url = reverse('category-list')
        data = {
            'name': 'Marketing',
            'description':
            'Marketing category involves creating, communicating, delivering, '
            'and exchanging offerings that have value for customers. It includes '
            'activities such as market research, advertising, and brand management.'
        }

        response = self.client.post(url, data, format='json')

        # Check if the task was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_cant_access_create(self):
        """Tests if the create view action diallows non staff users."""

        self.client.force_authenticate(user=self.user)

        url = reverse('category-list')
        data = {
            'name': 'Marketing',
            'description':
            'Marketing category involves creating, communicating, delivering, '
            'and exchanging offerings that have value for customers. It includes '
            'activities such as market research, advertising, and brand management.'
        }

        response = self.client.post(url, data, format='json')

        # Check if the permission is denied for non staff users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Update view
    def test_staff_can_access_update(self):
        """Tests if the update view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('category-detail', args=[self.financial_category.id])
        data = {
            'name': 'Financial Analysis',
            'description': 'Financial Analysis category involves assessing the '
            'financial health of the organization by analyzing '
            'financial statements, budgeting, forecasting, and '
            'providing insights for strategic decision-making.'
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_update(self):
        """Tests if the update view action disallows non staff users."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('category-detail', args=[self.financial_category.id])
        data = {
            'name': 'Financial Analysis',
            'description': 'Financial Analysis category involves assessing the '
            'financial health of the organization by analyzing '
            'financial statements, budgeting, forecasting, and '
            'providing insights for strategic decision-making.'
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Partial update view
    def test_staff_can_access_partial_update(self):
        """Tests if the partial update view action allows staff
        users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('category-detail', args=[self.financial_category.id])
        data = {
            'name': 'Financial Analysis',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cant_access_partial_update(self):
        """Tests if the partial update view action disallows non staff
        users."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('category-detail', args=[self.financial_category.id])
        data = {
            'name': 'Financial Analysis',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Destroy view
    def test_staff_can_access_destroy(self):
        """Tests if the destroy view action allows staff users."""

        self.user2.is_staff = True
        self.client.force_authenticate(user=self.user2)

        url = reverse('category-detail', args=[self.marketing_category.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_staff_cant_access_destroy(self):
        """Tests if the destroy view action disallows non staff users."""

        self.client.force_authenticate(user=self.user2)

        url = reverse('category-detail', args=[self.marketing_category.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
