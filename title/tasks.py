from django.db import IntegrityError, transaction
from django.apps import apps
from celery import shared_task
from .models import Chapter, ChapterImages, Team
from zipfile import ZipFile
from natsort import os_sorted
from cloudinary import uploader

Notification = apps.get_model(app_label="social", model_name="Notification")
Subscription = apps.get_model(app_label="social", model_name="Subscription")


@shared_task
def notify_users_of_new_title_status(title_id: int):
    try:
        Notification.objects.bulk_create(
            [
                Notification(
                    user_id=user_id,
                    title_id=title_id,
                    type=Notification.NotificationType.STATUS_CHANGED
                ) for user_id in Subscription.objects.filter(
                    title_id=title_id,
                    team__isnull=True
                ).values_list("user", flat=True)
            ],
            ignore_conflicts=True
        )
    except IntegrityError:
        pass


@shared_task
def notify_users_of_new_chapter(title_id: int, team_id: int, chapter_id: int):
    try:
        Notification.objects.bulk_create(
            [
                Notification(
                    user_id=user_id,
                    title_id=title_id,
                    team_id=team_id,
                    chapter_id=chapter_id,
                    type=Notification.NotificationType.NEW_CHAPTER
                ) for user_id in Subscription.objects.filter(
                    title_id=title_id,
                    team_id=team_id
                ).values_list("user", flat=True)
            ],
            ignore_conflicts=True
        )
    except IntegrityError:
        pass


@shared_task
def upload_chapter_images(chapter_id: int, user_id):
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except Chapter.DoesNotExist:
        return
    try:
        with transaction.atomic():
            with ZipFile(chapter.image_archive, "r") as archive:
                images = []
                for image in os_sorted(archive.namelist()):
                    images.append(image)
                ChapterImages.objects.bulk_create(
                    [
                        ChapterImages(
                            chapter_id=chapter_id,
                            image=uploader.upload_image(
                                archive.read(image),
                                folder=f"{chapter.title.slug}/c{chapter.id}"
                            )
                        ) for image in images
                    ]
                )
                archive.close()
                chapter.is_published = True
                chapter.save()
                Notification.objects.create(
                    user_id=user_id,
                    title=chapter.title,
                    team=chapter.team,
                    chapter=chapter,
                    type=Notification.NotificationType.CHAPTER_UPLOAD_SUCCESS
                )
                chapter.image_archive.delete()
                notify_users_of_new_chapter.delay(chapter.title.id, chapter.team.id, chapter.id)
    except IntegrityError:
        chapter.delete()
        try:
            Notification.objects.create(
                user_id=user_id,
                title=chapter.title,
                chapter=chapter,
                type=Notification.NotificationType.CHAPTER_UPLOAD_FAIL
            )
        except IntegrityError:
            return


@shared_task
def update_chapter_images(chapter_id: int, user_id):
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except Chapter.DoesNotExist:
        return
    chapter.is_published = False
    chapter.save()
    try:
        with transaction.atomic():
            ChapterImages.objects.filter(chapter=chapter).delete()
            with ZipFile(chapter.image_archive, "r") as archive:
                images = []
                for image in os_sorted(archive.namelist()):
                    images.append(image)
                ChapterImages.objects.bulk_create(
                    [
                        ChapterImages(
                            chapter_id=chapter_id,
                            image=uploader.upload_image(
                                archive.read(image),
                                folder=f"{chapter.title.slug}/c{chapter.id}"
                            )
                        ) for image in images
                    ]
                )
                archive.close()
                chapter.is_published = True
                chapter.save()
                Notification.objects.create(
                    user_id=user_id,
                    title=chapter.title,
                    team=chapter.team,
                    chapter=chapter,
                    type=Notification.NotificationType.CHAPTER_UPDATE_SUCCESS
                )
                chapter.image_archive.delete()
    except IntegrityError:
        try:
            if not chapter.is_published:
                chapter.is_published = True
                chapter.save()
            Notification.objects.create(
                user_id=user_id,
                title=chapter.title,
                chapter=chapter,
                type=Notification.NotificationType.CHAPTER_UPDATE_FAIL
            )
        except IntegrityError:
            return


@shared_task
def delete_chapter(chapter_id: int):
    try:
        chapter = Chapter.objects.get(id=chapter_id)
        chapter.delete()
    except Chapter.DoesNotExist:
        return


@shared_task
def delete_team(team_id: int):
    try:
        team = Team.objects.get(id=team_id)
        team.delete()
    except Team.DoesNotExist:
        return
