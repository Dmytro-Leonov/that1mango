from rest_framework import serializers
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import List, Subscription, ListTitle, Friend, Notification, Comment, CommentVote
from django.apps import apps

Title = apps.get_model(app_label="title", model_name="Title")
Team = apps.get_model(app_label="title", model_name="Team")
User = apps.get_model(app_label="users", model_name="User")
Chapter = apps.get_model(app_label="title", model_name="Chapter")


class ListCreateSerializer(serializers.ModelSerializer):
    hidden = serializers.BooleanField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Поле обязательно"
        }
    )
    name = serializers.CharField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Имя пользователя не попало на сервер"
        },
        validators=[
            MinLengthValidator(2, message="Название должно состоять минимум из 2 символов"),
            MaxLengthValidator(30, message="Название не должно превышать 30 символов")
        ]
    )

    class Meta:
        model = List
        fields = ("name", "hidden")


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ("id", "user", "name", "hidden", "titles_count")


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("title", "team")


class ListTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListTitle
        fields = ("list", "title")


class ListTitleRUDSerializer(serializers.Serializer):
    list = serializers.IntegerField(required=False)

    class Meta:
        fields = ("list",)


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if not obj and self.allow_blank:
            return obj
        return {"slug": obj, "name": self._choices[obj]}

    def to_internal_value(self, data):
        if not data and self.allow_blank:
            return None
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class ListTitleListSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    poster = serializers.ImageField()
    title_type = ChoiceField(choices=Title.TitleType.choices)
    title_status = ChoiceField(choices=Title.TitleStatus.choices)
    total_rating = serializers.FloatField()
    added = serializers.DateTimeField()
    user_rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            "id", "name", "slug", "poster", "title_type", "title_status", "total_rating", "user_rating", "added",
            "age_rating"
            )


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ("friend",)


class NotificationFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "profile_pic")


class NotificationTitleSerializer(serializers.ModelSerializer):
    title_status = ChoiceField(choices=Title.TitleStatus.choices)

    class Meta:
        model = Title
        fields = ("name", "slug", "poster", "title_status", "age_rating")


class NotificationTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "slug", "picture")


class NotificationChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ("id", "name", "volume_number", "chapter_number")


class NotificationSerializer(serializers.ModelSerializer):
    friend = NotificationFriendSerializer()
    title = NotificationTitleSerializer()
    team = NotificationTeamSerializer()
    chapter = NotificationChapterSerializer()
    type = ChoiceField(choices=Notification.NotificationType.choices, required=False)

    class Meta:
        model = Notification
        fields = ("id", "user", "friend", "title", "team", "chapter", "type", "created_at", "is_read")


class DeleteNotificationsSerializer(serializers.Serializer):
    is_read = serializers.BooleanField()

    class Meta:
        fields = ("is_read",)


class FriendRequestNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("user",)


class CreateDefaultListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ("id", "name")


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "profile_pic")


class CommentListSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    vote = serializers.BooleanField(required=False)
    count_replies = serializers.IntegerField(required=False)
    is_author = serializers.BooleanField(required=False)

    class Meta:
        model = Comment
        fields = (
            "id", "user", "creation_date", "comment", "is_deleted", "vote", "likes", "dislikes",
            "count_replies", "is_author",
        )


class CommentVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentVote
        fields = (
            "comment", "vote",
        )


class CommentSerializer(serializers.ModelSerializer):
    is_deleted = serializers.BooleanField(default=False)
    comment = serializers.CharField(
        error_messages={
            "blank": "Комментарий не должен быть пустым"
        }
    )

    class Meta:
        model = Comment
        fields = ("id", "title", "reply_to", "comment", "creation_date", "is_deleted")


class CommentUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    is_deleted = serializers.BooleanField(default=False)

    class Meta:
        model = Comment
        fields = ("id", "comment", "is_deleted")
