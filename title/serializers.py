from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import (
    Title, ReleaseFormat, Rating, Publisher, Person, Keyword, TitleRating, TitlePerson, UserTitleRating,
    Chapter, Team, TeamParticipant
)
from django.apps import apps

Notification = apps.get_model(app_label="social", model_name="Notification")
allowed_extensions = ["zip"]
ALLOWED_ARCHIVE_SIZE = 1024 ** 2 * 150  # 500 mb


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return {"slug": obj, "name": self._choices[obj]}

    def to_internal_value(self, data):
        if data == "" and self.allow_blank:
            return ""
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class ChoiceValueField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == "" and self.allow_blank:
            return ""
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    profile_pic = serializers.ImageField()

    class Meta:
        fields = ("id", "username", "profile_pic")


class TeamParticipantSerializer(serializers.Serializer):
    user = UserSerializer()
    roles = serializers.ListSerializer(child=ChoiceField(choices=TeamParticipant.Role.choices))

    class Meta:
        fields = ("user", "roles")


class TeamSerializer(serializers.ModelSerializer):
    participants = TeamParticipantSerializer(source="team_participants", many=True, read_only=True)
    total_chapters = serializers.IntegerField(required=False)
    total_likes = serializers.IntegerField(required=False)
    total_titles = serializers.IntegerField(required=False)
    picture = serializers.ImageField(required=False)

    class Meta:
        model = Team
        fields = (
            "id", "participants", "name", "slug", "picture", "description", "total_chapters", "total_likes",
            "total_titles"
        )


class ReleaseFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseFormat
        fields = ("slug", "name")


class PublisherSerializer(serializers.ModelSerializer):
    alternative_names = serializers.ListField(child=serializers.CharField())
    picture = serializers.ImageField(required=False)

    class Meta:
        model = Publisher
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    alternative_names = serializers.ListField(child=serializers.CharField())
    picture = serializers.ImageField(required=False)

    class Meta:
        model = Person
        fields = "__all__"


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ("type", "slug", "name")


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("mark",)


class TitleRatingSerializer(serializers.ModelSerializer):
    rating = RatingSerializer()

    class Meta:
        model = TitleRating
        fields = ("rating", "amount")


class PublisherTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ("slug", "name", "picture")


class PersonTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name", "picture")


class TitlePersonSerializer(serializers.ModelSerializer):
    person = PersonTitleSerializer()
    title_role = ChoiceField(choices=TitlePerson.TitleRole.choices)

    class Meta:
        model = TitlePerson
        fields = ("person", "title_role")


class TitleTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "slug", "picture")


class RandomTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ("slug",)


class TitleDetailsSerializer(serializers.ModelSerializer):
    age_rating = ChoiceField(choices=Title.TitleAgeRating.choices)
    title_type = ChoiceField(choices=Title.TitleType.choices)
    title_status = ChoiceField(choices=Title.TitleStatus.choices)
    release_format = ReleaseFormatSerializer(many=True)
    publisher = PublisherTitleSerializer(many=True)
    person = TitlePersonSerializer(source="persons_of_title", many=True)
    keywords = KeywordSerializer(many=True)
    title_rating = TitleRatingSerializer(source="ratings_of_title", many=True)
    likes = serializers.IntegerField()
    chapter_count = serializers.IntegerField()
    teams = TitleTeamSerializer(many=True)
    subscribed = serializers.BooleanField()

    class Meta:
        model = Title
        fields = "__all__"


class TitleListSerializer(serializers.ModelSerializer):
    age_rating = ChoiceField(choices=Title.TitleAgeRating.choices)
    title_type = ChoiceField(choices=Title.TitleType.choices)
    total_rating = serializers.FloatField()

    class Meta:
        model = Title
        fields = ("poster", "age_rating", "name", "title_type", "slug", "total_rating")


class LikeChapterSerializer(serializers.Serializer):
    chapter_id = serializers.IntegerField()

    class Meta:
        fields = ("id",)


class RateTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = UserTitleRating
        fields = ("title", "rating")


class ChapterSerializer(serializers.ModelSerializer):
    liked_by_user = serializers.BooleanField()

    class Meta:
        model = Chapter
        fields = ("id", "volume_number", "chapter_number", "name", "date_added", "likes", "liked_by_user")


class ChapterAnonymousSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ("id", "team", "volume_number", "chapter_number", "name", "date_added", "likes")


class ChapterTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "slug", "picture")


class ChapterTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ("name", "slug", "poster", "age_rating")


class LatestChaptersSerializer(serializers.ModelSerializer):
    title = ChapterTitleSerializer()
    team = ChapterTeamSerializer()

    class Meta:
        model = Chapter
        fields = ("title", "name", "volume_number", "chapter_number", "date_added", "team")


class InviteToTeamSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=Notification.NotificationType.choices,
        default=Notification.NotificationType.JOIN_TEAM_REQUEST
    )

    class Meta:
        model = Notification
        fields = ("user", "team", "type")


class TeamParticipantRUDSerializer(serializers.Serializer):
    team = serializers.IntegerField()
    user = serializers.IntegerField()
    roles = serializers.ListSerializer(
        child=serializers.ChoiceField(choices=TeamParticipant.Role.choices),
        required=False
    )

    class Meta:
        model = TeamParticipant
        fields = ("team", "user", "roles")


class TitleSearchSerializer(serializers.ModelSerializer):
    title_type = ChoiceValueField(choices=Title.TitleType.choices)
    total_rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ("slug", "name", "english_name", "total_rating", "poster", "title_type")


class PersonSearchSerializer(serializers.ModelSerializer):
    alternative_names = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Person
        fields = ("id", "name", "alternative_names", "picture")


class PublisherSearchSerializer(serializers.ModelSerializer):
    alternative_names = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Publisher
        fields = ("slug", "name", "alternative_names", "picture")


class TeamSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("slug", "name", "picture")


class PopularNowTitlesSerializer(serializers.ModelSerializer):
    title_type = ChoiceField(choices=Title.TitleType.choices)
    likes = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ("name", "slug", "poster", "title_type", "likes", "age_rating")


class UploadChapterSerializer(serializers.ModelSerializer):
    image_archive = serializers.FileField(
        error_messages={
            "blank": "Архив не может быть пустым",
            "invalid": "Некорректный архив"
        }
    )

    def validate_image_archive(self, image_archive):
        if image_archive.name.split(".")[-1].lower() not in allowed_extensions:
            raise serializers.ValidationError(f"Допустимые расширения: {allowed_extensions}")
        elif image_archive.size > ALLOWED_ARCHIVE_SIZE:
            raise serializers.ValidationError(f"Архив должен весить не более {ALLOWED_ARCHIVE_SIZE / (1024 ** 2)} МБ")
        return image_archive

    class Meta:
        model = Chapter
        fields = ("title", "team", "name", "volume_number", "chapter_number", "image_archive")
        validators = [
            UniqueTogetherValidator(
                queryset=Chapter.objects.all(),
                fields=["title", "team", "volume_number", "chapter_number"],
                message="К данному тайтлу уже добавлена такая глава от этой команды",
            )
        ]


class UpdateChapterSerializer(serializers.ModelSerializer):
    image_archive = serializers.FileField(
        required=False,
        error_messages={
            "invalid": "Некорректный архив"
        }
    )

    def validate_image_archive(self, image_archive):
        if image_archive and image_archive.name.split(".")[-1].lower() not in allowed_extensions:
            raise serializers.ValidationError(f"Допустимые расширения: {allowed_extensions}")
        elif image_archive.size > ALLOWED_ARCHIVE_SIZE:
            raise serializers.ValidationError(f"Архив должен весить не более {ALLOWED_ARCHIVE_SIZE / (1024 ** 2)} МБ")
        return image_archive

    class Meta:
        model = Chapter
        fields = ("name", "volume_number", "chapter_number", "image_archive")


class ChapterDetailTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ("name", "slug")


class ChapterDetailTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "slug", "picture")


class CloudinaryField(serializers.Field):
    def to_representation(self, value):
        return value.url


class ChapterDetailSerializer(serializers.ModelSerializer):
    title = ChapterDetailTitleSerializer(many=False)
    team = ChapterDetailTeamSerializer(many=False)
    images = serializers.ListField(child=CloudinaryField())
    liked_by_user = serializers.BooleanField()

    class Meta:
        model = Chapter
        fields = ("id", "title", "team", "volume_number", "chapter_number", "name", "images", "liked_by_user")


class AllTitleTeamChaptersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ("volume_number", "chapter_number")
