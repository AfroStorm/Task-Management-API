# api/management/commands/notify_due_dates.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from api.models import Task


class Command(BaseCommand):
    """Send notifications for due dates approaching in 7 days."""

    help = 'Send notifications for due dates approaching in 7 days'

    def handle(self, *args, **options):
        current_date = timezone.now()
        seven_days_later = current_date + timezone.timedelta(days=7)

        due_dates_approaching = Task.objects.filter(
            due_date__lte=seven_days_later,
            due_date__gte=current_date
        )

        for task in due_dates_approaching:

            subject = 'Task due date is approaching'
            message = f'''The deadline for the task "{task.title}" with the
                          ID: {task.id} is approaching! Due-date:
                          {task.due_date}, Current-date: {current_date}.'''

            from_email = 'admin@it-backends.com'

            recipient_list = [
                member.email for member in task.task_group.team_members.all()
            ]

            send_mail(subject, message, from_email, recipient_list)
