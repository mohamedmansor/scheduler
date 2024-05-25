from celery import shared_task

from webtask_scheduler.users.models import User


@shared_task
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()
