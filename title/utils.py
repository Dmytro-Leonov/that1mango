from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.pagination import LimitOffsetPagination
from .models import TeamParticipant
from zipfile import ZipFile, BadZipFile
from io import BytesIO
from PIL import Image


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsTeamAdmin(BasePermission):
    message = "Только администратор команды может управлять ей"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_anonymous:
            try:
                tp = TeamParticipant.objects.get(user=request.user, team=obj)
                return TeamParticipant.Role.ADMIN in tp.roles
            except TeamParticipant.DoesNotExist:
                return False
        else:
            return False


class CanManageParticipants(BasePermission):
    message = "Только администратор команды может управлять учасниками."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous:
            try:
                tp = TeamParticipant.objects.get(user=request.user, team=obj.team)
                if request.user.id == obj.user.id and request.method == "DELETE":
                    return True
                return tp.roles and TeamParticipant.Role.ADMIN in tp.roles
            except TeamParticipant.DoesNotExist:
                return False
        else:
            return False


class CanUpdateChapter(BasePermission):
    message = "Главы может изменять только администратор команды или учасник с ролью 'Загрузчик'"

    def has_object_permission(self, request, view, obj):
        try:
            tp = TeamParticipant.objects.get(user=request.user, team=obj.team)
            return tp.roles and (TeamParticipant.Role.ADMIN in tp.roles or TeamParticipant.Role.UPLOADER in tp.roles)
        except TeamParticipant.DoesNotExist:
            return False


def validate_image_archive(image_archive) -> int:
    file_path = image_archive if type(image_archive) == InMemoryUploadedFile \
        else image_archive.temporary_file_path()
    try:
        with ZipFile(file_path, "r") as archive:
            files = archive.namelist()
            if len(files) == 0:
                raise BadZipFile
            for image in files:
                if image.split(".")[-1].lower() not in settings.ALLOWED_CHAPTER_IMAGE_EXTENSIONS:
                    return 1
                im = BytesIO(archive.read(image))
                Image.open(im).verify()
                if im.getbuffer().nbytes > settings.ALLOWED_CHAPTER_IMAGE_SIZE:
                    return 2
    except (BadZipFile, Image.UnidentifiedImageError, IOError):
        return 3


class NewChaptersPagination(LimitOffsetPagination):
    default_limit = 10


class NotMatureException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Авторизируйтесь, чтобы иметь доступ к этой главе"
    default_code = "data"


class NotAuthenticatedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Вы должны быть старше 18 лет, чтобы иметь доступ к этой главе"
    default_code = "data"
