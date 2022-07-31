from rest_framework.permissions import BasePermission


class UserDeleteWriteListTitlePermission(BasePermission):
    message = "Только владелец аккаунта может управлять своими списками"

    def has_object_permission(self, request, view, obj):
        return obj.list.user == request.user


class UserDeleteWritePermission(BasePermission):
    message = "Только владелец аккаунта может управлять своими списками"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class NotificationPermission(BasePermission):
    message = "Только владелец аккаунта может управлять своими уведомлениями"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CommentPermission(BasePermission):
    message = "Только владелец аккаунта может управлять своими комментариями"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
