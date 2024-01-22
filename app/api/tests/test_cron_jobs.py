from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from api import models, signals
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.conf import settings


User = get_user_model()


class NotifyDueDatesTest(TestCase):
    def setUp(self):

        # Deactivate signal handlers
        post_save.disconnect(signals.create_task_group, sender=models.Task)
        post_save.disconnect(signals.create_or_update_profile, sender=User)

        # Creating user instance 1
        self.user = User.objects.create(
            email='eliasmaloa1@gmail.com',
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

        # Creating userprofile instance 1
        self.userprofile = models.UserProfile.objects.create(
            owner=self.user,
            first_name='Peter',
            last_name='Pahn',
            phone_number=int('0163557799'),
            email=self.user.email,
            position=self.human_resource_position
        )

        # Task group instance
        self.task_group = models.TaskGroup.objects.create(
            name='The first TaskGroup'
        )

        self.task_group.suggested_positions.set(
            [self.human_resource_position]
        )
        self.task_group.team_members.set([self.userprofile])

        # Task group instance 2
        self.task_group2 = models.TaskGroup.objects.create(
            name='The second TaskGroup'
        )

        self.task_group2.suggested_positions.set(
            [self.human_resource_position]
        )
        self.task_group2.team_members.set([self.userprofile])

        # task with a due date in 5 days
        self.task_due_soon = models.Task.objects.create(
            title='Task Due Soon',
            due_date=(timezone.now() + timezone.timedelta(days=5)).date(),
            task_group=self.task_group
        )

        # task with a due date in 10 days
        self.task_not_due_soon = models.Task.objects.create(
            title='Task Not Due Soon',
            due_date=(timezone.now() + timezone.timedelta(days=10)).date(),
            task_group=self.task_group2
        )

    def test_notify_due_dates_command(self):
        # Call the management command
        call_command('notify_due_dates')

        # Check if the email was sent to the correct recipient
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, 'Task due date is approaching')
        self.assertIn(str(self.task_due_soon.due_date), sent_email.body)
        self.assertIn(self.task_due_soon.title, sent_email.body)
        self.assertEqual(sent_email.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(sent_email.to, [self.userprofile.email])

        # Check if the email was not sent for the task not due soon
        self.assertNotIn(self.task_not_due_soon.title, sent_email.body)
