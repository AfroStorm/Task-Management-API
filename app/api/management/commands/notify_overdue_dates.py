from typing import Any
from django.core.management import BaseCommand
from django.utils import timezone
from api import models
from django.core.mail import send_mail


class Command(BaseCommand):
    """Send notifications for overdue dates."""

    help = 'Send notifications for overdue dates.'

    def handle(self, *args: Any, **options: Any) -> str | None:
        current_date = (timezone.now()).date()

        overdue_dates = models.Task.objects.filter(
            due_date__lt=current_date
        )

        for task in overdue_dates:
            recipient_list = [
                member.email for member in task.task_group.team_members.all()
            ]

            subject = 'The date of the task is overdue!'
            message = f'''The deadline for the task "{task.title}" with the
                       ID: {task.id} is overdue! Due-date: {task.due_date},
                       Current-date: {current_date}.'''
            from_email = 'admin@it-backends.com'

            send_mail(subject, message, from_email, recipient_list)
