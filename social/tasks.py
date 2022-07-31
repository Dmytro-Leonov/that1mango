from celery import shared_task
from .models import Notification, Comment


@shared_task
def notify_user_of_comment_reply(comment_id: int, user_id: int):

    try:
        comment = Comment.objects.get(id=comment_id)
        if comment.user.id != user_id:
            Notification.objects.create(
                user=comment.user, title=comment.title, type=Notification.NotificationType.COMMENT_REPLY
            )
    except Comment.DoesNotExist:
        pass
