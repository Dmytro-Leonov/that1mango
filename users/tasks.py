from celery import shared_task
from django.core.mail import send_mail
from .models import User


@shared_task
def send_email(subject, message, recipient_list, fail_silently=True):
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=recipient_list,
        fail_silently=fail_silently
    )


@shared_task
def delete_inactive(user_id: int):
    try:
        user = User.objects.get(id=user_id)
        if not user.is_active:
            user.delete()
    except User.DoesNotExist:
        pass
