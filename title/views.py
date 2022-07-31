from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import IntegrityError, transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, F, Value, Count, Exists, OuterRef, FloatField, IntegerField
from django.db.models.functions import Greatest, Coalesce
from .models import (
    Title, Rating, UserTitleRating, Chapter, Keyword, ReleaseFormat, Person, Publisher, Team, TeamParticipant,
    ChapterLikes
)
from .serializers import (
    TitleDetailsSerializer, TitleListSerializer, LikeChapterSerializer, RateTitleSerializer, ChapterSerializer,
    ChapterAnonymousSerializer, KeywordSerializer, ReleaseFormatSerializer, PersonSerializer, PublisherSerializer,
    TeamSerializer, RandomTitleSerializer, LatestChaptersSerializer, InviteToTeamSerializer, ChapterDetailSerializer,
    TeamParticipantRUDSerializer, TitleSearchSerializer, PersonSearchSerializer, PublisherSearchSerializer,
    TeamSearchSerializer, PopularNowTitlesSerializer, UploadChapterSerializer, UpdateChapterSerializer,
    AllTitleTeamChaptersSerializer
)
from django_filters import rest_framework as filters
from .filters import TitleFilter, RelatedTitleFilter
from random import choice
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from .tasks import upload_chapter_images, update_chapter_images, delete_chapter, delete_team
from .utils import (
    ReadOnly, IsTeamAdmin, CanManageParticipants, CanUpdateChapter, validate_image_archive, NewChaptersPagination,
    NotMatureException, NotAuthenticatedException
)
import datetime
from dateutil.relativedelta import relativedelta

Subscription = apps.get_model(app_label="social", model_name="Subscription")
Notification = apps.get_model(app_label="social", model_name="Notification")


class TitleList(generics.ListAPIView):
    queryset = Title.objects.annotate(
        total_rating=Coalesce(
            Sum(
                F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
            ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
            output_field=FloatField()
        )
    )
    serializer_class = TitleListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TitleFilter


class TitleDetails(APIView):
    def get(self, request, **kwargs):
        slug = self.kwargs.get("slug")
        subs = []
        if self.request.user.is_anonymous:
            title = get_object_or_404(Title.objects.annotate(
                likes=Coalesce(Sum("chapters_of_title__likes"), 0),
                subscribed=Value(False)
            ), slug=slug)
        else:
            title = get_object_or_404(Title.objects.annotate(
                likes=Coalesce(Sum("chapters_of_title__likes"), 0),
                subscribed=Exists(
                    Title.objects.filter(
                        title_subscriptions__user=self.request.user,
                        title_subscriptions__title=OuterRef("id"),
                        title_subscriptions__team__isnull=True
                    )
                )
            ), slug=slug)

            subs = list(Subscription.objects.filter(
                Q(user=self.request.user) &
                Q(title=title.id) &
                Q(team__isnull=False)
            ).values_list("team", flat=True))

        return Response({
            "title": TitleDetailsSerializer(title, context={'request': request}).data,
            "subscribed_to_teams": subs,
        }, status=status.HTTP_200_OK)


class LikeChapter(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeChapterSerializer

    def post(self, request, *args, **kwargs):
        try:
            ChapterLikes.objects.create(
                user_id=self.request.user.id,
                chapter_id=request.data.get("chapter_id"),
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"data": "Ваш голос учтен"}, status=status.HTTP_200_OK)


class RateTitle(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RateTitleSerializer

    def post(self, request, *args, **kwargs):
        try:
            UserTitleRating.objects.create(
                user_id=self.request.user.id,
                title_id=request.data.get("title"),
                rating=get_object_or_404(Rating, mark=request.data.get("rating"))
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"data": "Ваш голос учтен"}, status=status.HTTP_200_OK)


class RateTitleGet(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RateTitleSerializer

    def post(self, request, *args, **kwargs):
        rating = UserTitleRating.objects.filter(
            user_id=self.request.user.id,
            title_id=request.data.get("title")
        ).first()
        if rating:
            return Response(data={"rating": rating.rating.id}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class RateTitleDestroy(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RateTitleSerializer

    def destroy(self, request, *args, **kwargs):
        rating = UserTitleRating.objects.filter(
            user_id=self.request.user.id,
            title_id=request.data.get("title")
        ).first()
        if rating:
            rating.delete()
            return Response(data={"data": "Оценка удалена"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class ChapterListForTeam(generics.ListAPIView):
    pagination_class = None

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return ChapterAnonymousSerializer
        return ChapterSerializer

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        team_id = self.kwargs.get("team_id")
        if self.request.user.is_anonymous:
            return Chapter.objects.filter(title_id=title_id, team_id=team_id, is_published=True)
        return Chapter.objects.filter(title_id=title_id, team_id=team_id, is_published=True).annotate(
            liked_by_user=Exists(
                ChapterLikes.objects.filter(chapter_id=OuterRef("id"), user_id=self.request.user.id)
            )
        )


class GetAllFilteringValues(generics.ListAPIView):
    pagination_class = None

    @method_decorator(cache_page(60 * 60 * 24))  # cache for one day
    def list(self, request, *args, **kwargs):
        def serialize(choices):
            return [{"slug": obj[0], "name": obj[1]} for obj in choices]

        data = {
            "age": serialize(Title.TitleAgeRating.choices),
            "type": serialize(Title.TitleType.choices),
            "status": serialize(Title.TitleStatus.choices),
            "release_format": ReleaseFormatSerializer(ReleaseFormat.objects.all(), many=True).data,
            "keyword": KeywordSerializer(Keyword.objects.all().order_by("name"), many=True).data
        }
        return Response(data)


class PersonCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    parser_classes = [MultiPartParser, FormParser]


class PersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ReadOnly | IsAdminUser]
    serializer_class = PersonSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, queryset=None, **kwargs):
        pk = self.kwargs.get("person_id")
        return get_object_or_404(Person, id=pk)


class DeletePersonPicture(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("person_id")
        get_object_or_404(Team, id=pk).picture.delete()
        return Response(status=status.HTTP_200_OK)


class PersonTitlesGetView(generics.ListAPIView):
    serializer_class = TitleListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RelatedTitleFilter

    def get_queryset(self):
        person_id = self.kwargs.get("person_id")
        return Title.objects.filter(persons_of_title__person=person_id).annotate(
            total_rating=Coalesce(
                Sum(
                    F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
                ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
                output_field=FloatField()
            )
        )


# views for publishers
class PublisherCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    parser_classes = [MultiPartParser, FormParser]


class PublisherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ReadOnly | IsAdminUser]
    serializer_class = PublisherSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, queryset=None, **kwargs):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Publisher, slug=slug)


class DeletePublisherPicture(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("publisher_id")
        get_object_or_404(Team, id=pk).picture.delete()
        return Response(status=status.HTTP_200_OK)


class PublisherTitlesGetView(generics.ListAPIView):
    serializer_class = TitleListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RelatedTitleFilter

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return Title.objects.filter(publishers_of_title__publisher__slug=slug).annotate(
            total_rating=Coalesce(
                Sum(
                    F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
                ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
                output_field=FloatField()
            )
        )


# views for teams
class TeamCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    team = serializer.save()
                    Team.participants.through.objects.create(
                        user=self.request.user, team=team, roles=[TeamParticipant.Role.ADMIN]
                    )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"data": "Ошибка при создании команды"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView, IsTeamAdmin):
    permission_classes = [IsTeamAdmin]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TeamSerializer

    def get_object(self, queryset=None, **kwargs):
        slug = self.kwargs.get("slug")

        team = get_object_or_404(
            Team.objects.annotate(
                total_titles=Coalesce(
                    Count("titles_of_team", distinct=True), 0
                ),
                total_chapters=Coalesce(
                    Count("chapters_of_team", distinct=True), 0
                ),
                total_likes=Value(
                    Chapter.objects.filter(team__slug=slug).aggregate(
                        total_likes=Sum("likes")
                    )["total_likes"],
                    output_field=IntegerField()
                )
            ), slug=slug)

        self.check_object_permissions(self.request, team)
        return team

    def destroy(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        team = get_object_or_404(Team, slug=slug)
        self.check_object_permissions(self.request, team)
        delete_team.delay(team.id)
        return Response(
            data={"data": "Команда со всеми переводими удалится в ближайшее время"},
            status=status.HTTP_204_NO_CONTENT
        )

    def patch(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        team = get_object_or_404(Team, slug=slug)
        self.check_object_permissions(self.request, team)
        serializer = self.serializer_class(team, partial=True, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTeamPicture(APIView, IsTeamAdmin):
    permission_classes = [IsAuthenticated, IsTeamAdmin]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("team_id")
        team = get_object_or_404(Team, id=pk)
        self.check_object_permissions(self.request, team)
        team.picture.delete()
        return Response(status=status.HTTP_200_OK)


class TeamTitlesGetView(generics.ListAPIView):
    serializer_class = TitleListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RelatedTitleFilter

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return Title.objects.filter(teams_of_title__team__slug=slug).annotate(
            total_rating=Coalesce(
                Sum(
                    F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
                ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
                output_field=FloatField()
            )
        )


class InviteToTeam(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InviteToTeamSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data.get("user")
            team_id = serializer.data.get("team")
            notification_type = Notification.NotificationType.JOIN_TEAM_REQUEST
            if Notification.objects.filter(user_id=user_id, team_id=team_id, type=notification_type):
                return Response(
                    data={"data": "Вы уже пригласили этого пользователя в команду"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Notification.objects.create(user_id=user_id, team_id=team_id, type=notification_type)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamParticipantUpdateDestroy(APIView, CanManageParticipants):
    permission_classes = [IsAuthenticated, CanManageParticipants]
    serializer_class = TeamParticipantRUDSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            team_id = serializer.data.get("team")
            user_id = serializer.data.get("user")
            roles = serializer.data.get("roles")
            tp = get_object_or_404(TeamParticipant, team_id=team_id, user_id=user_id)
            self.check_object_permissions(self.request, tp)

            if self.request.user.id != user_id or TeamParticipant.Role.ADMIN in roles:
                tp.roles = roles
                tp.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            count_admins = TeamParticipant.objects.filter(
                team_id=team_id, roles__icontains=TeamParticipant.Role.ADMIN
            ).count()
            if count_admins > 1:
                tp.roles = roles
                tp.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    data={"data": "Вы не можете убрать у себя админку, если вы единственный администратор"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            team_id = serializer.data.get("team")
            user_id = serializer.data.get("user")
            tp = get_object_or_404(TeamParticipant, team_id=team_id, user_id=user_id)
            self.check_object_permissions(self.request, tp)
            try:
                with transaction.atomic():
                    if self.request.user.id != user_id:
                        tp.delete()
                        Notification.objects.create(
                            user_id=user_id,
                            team_id=team_id,
                            type=Notification.NotificationType.TEAM_KICK
                        )
                        return Response(status=status.HTTP_204_NO_CONTENT)

                    team_participants = TeamParticipant.objects.filter(team_id=team_id)
                    count_admins = 0
                    count_members = len(team_participants)
                    for participant in team_participants:
                        if participant.roles and TeamParticipant.Role.ADMIN in participant.roles:
                            count_admins += 1

                    if count_admins > 1:
                        tp.delete()
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    elif count_members == 1:
                        tp.delete()
                        if Chapter.objects.filter(team_id=team_id).count() == 0:
                            Team.objects.get(id=team_id).delete()
                            return Response(
                                data={"data": "Вы покинули команду и она была удалена"},
                                status=status.HTTP_204_NO_CONTENT
                            )
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response(
                            data={
                                "data": "Вы не можете покинуть команду, "
                                        "если вы единственный администратор и в команде есть другие учасники"
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
            except (IntegrityError, Team.DoesNotExist):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RandomTitleView(generics.RetrieveAPIView):
    serializer_class = RandomTitleSerializer

    def get_object(self):
        return get_object_or_404(Title, id=choice(Title.objects.values_list('id', flat=True)))


class TitleSearchView(generics.ListAPIView):
    serializer_class = TitleSearchSerializer

    def get_queryset(self):
        name = self.kwargs.get("name")
        return Title.objects.filter(
            Q(name__icontains=name) | Q(english_name__icontains=name) | Q(alternative_names__icontains=name)
        ).annotate(
            total_rating=Coalesce(
                Sum(
                    F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
                ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
                output_field=FloatField()
            )
        )


class PersonSearchView(generics.ListAPIView):
    serializer_class = PersonSearchSerializer

    def get_queryset(self):
        name = self.kwargs.get("name")
        return Person.objects.filter(Q(name__icontains=name) | Q(alternative_names__icontains=name))


class PublisherSearchView(generics.ListAPIView):
    serializer_class = PublisherSearchSerializer

    def get_queryset(self):
        name = self.kwargs.get("name")
        return Publisher.objects.filter(Q(name__icontains=name) | Q(alternative_names__icontains=name))


class TeamSearchView(generics.ListAPIView):
    serializer_class = TeamSearchSerializer

    def get_queryset(self):
        name = self.kwargs.get("name")
        return Team.objects.filter(Q(name__icontains=name))


class NewTitles(generics.ListAPIView):
    pagination_class = None
    serializer_class = TitleListSerializer
    queryset = Title.objects.annotate(
        total_rating=Coalesce(
            Sum(
                F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
            ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
            output_field=FloatField()
        )
    ).order_by("-id")[:20]


class NewChapters(generics.ListAPIView):
    serializer_class = LatestChaptersSerializer
    pagination_class = NewChaptersPagination
    queryset = Chapter.objects.filter(
        date_added__gte=timezone.now() - datetime.timedelta(days=7),
        is_published=True
    ).order_by("-id")


class PopularNowTitles(generics.ListAPIView):
    serializer_class = PopularNowTitlesSerializer
    queryset = Title.objects.filter(
        chapters_of_title__likes_for_chapter__date_added__gte=timezone.now() - datetime.timedelta(days=30)
    ).annotate(
        likes=Count("*")
    ).order_by("-likes")[:20]


class UploadChapter(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadChapterSerializer
    queryset = Chapter.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            title = serializer.validated_data.get("title")
            team = serializer.validated_data.get("team")
            image_archive = serializer.validated_data.get("image_archive")
            if not title.licensed:
                # check if user can upload chapter
                try:
                    tp = TeamParticipant.objects.get(user_id=user, team=team)
                    if tp.roles and \
                            TeamParticipant.Role.ADMIN not in tp.roles and TeamParticipant.Role.UPLOADER not in tp.roles:
                        return Response(
                            data={
                                "data": "Главы может добавлять только администратор команды или учасник с ролью 'Загрузчик'"
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except TeamParticipant.DoesNotExist:
                    return Response(
                        data={"data": "Вы не можете добавить главу за команду, в которой не состоите"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # validate archive
                match validate_image_archive(image_archive):
                    case 1:
                        return Response(
                            data={"data": f"Допустимые расширения страниц: {settings.ALLOWED_CHAPTER_IMAGE_EXTENSIONS}"},
                            status=status.HTTP_400_BAD_REQUEST)
                    case 2:
                        return Response(
                            data={"image_archive": f"Изображения не должны превышать "
                                                   f"{settings.ALLOWED_CHAPTER_IMAGE_SIZE / (1024 ** 2)} МБ "},
                            status=status.HTTP_400_BAD_REQUEST)
                    case 3:
                        return Response(
                            data={"image_archive": f"Некорректные/поврежденные данные в архиве"},
                            status=status.HTTP_400_BAD_REQUEST)

                # upload chapter and create task to load images
                try:
                    chapter = serializer.save()
                    upload_chapter_images.delay(chapter.id, user.id)
                    return Response(status=status.HTTP_201_CREATED)
                except IntegrityError:
                    return Response(data={"data": "Ошибка создания главы"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    data={"data": "К лицензированому тайтлу нельзя добавлять главы"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UpdateChapter(generics.UpdateAPIView, CanUpdateChapter):
    permission_classes = [IsAuthenticated, CanUpdateChapter]
    serializer_class = UpdateChapterSerializer
    queryset = Chapter.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            volume_number = serializer.validated_data.get("volume_number")
            chapter_number = serializer.validated_data.get("chapter_number")
            image_archive = serializer.validated_data.get("image_archive")
            chapter_id = self.kwargs.get("chapter_id")
            chapter = get_object_or_404(Chapter, id=chapter_id)
            if not chapter.is_published:
                return Response(data={"data": "Нельзя редактировать главу, которая еще не опубликована"})
            self.check_object_permissions(self.request, chapter)
            if image_archive:
                match validate_image_archive(image_archive):
                    case 1:
                        return Response(
                            data={
                                "data": f"Допустимые расширения страниц: {settings.ALLOWED_CHAPTER_IMAGE_EXTENSIONS}"},
                            status=status.HTTP_400_BAD_REQUEST)
                    case 2:
                        return Response(
                            data={"image_archive": f"Изображения не должны превышать "
                                                   f"{settings.ALLOWED_CHAPTER_IMAGE_SIZE / (1024 ** 2)} МБ "},
                            status=status.HTTP_400_BAD_REQUEST)
                    case 3:
                        return Response(
                            data={"image_archive": f"Некорректные/поврежденные данные в архиве"},
                            status=status.HTTP_400_BAD_REQUEST)

            try:
                chapter.name = name
                chapter.volume_number = volume_number
                chapter.chapter_number = chapter_number
                chapter.image_archive = image_archive
                chapter.save()
                # replace image archive
                if image_archive:
                    update_chapter_images.delay(chapter.id, self.request.user.id)
                return Response(status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(data={"data": "К данному тайтлу уже добавлена такая глава от этой команды"},
                                status=status.HTTP_400_BAD_REQUEST
                                )
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteChapter(generics.DestroyAPIView, CanUpdateChapter):
    permission_classes = [IsAuthenticated, CanUpdateChapter]
    queryset = Chapter.objects.all()

    def destroy(self, request, *args, **kwargs):
        chapter = get_object_or_404(Chapter, id=self.kwargs.get("chapter_id"))
        self.check_object_permissions(self.request, chapter)
        if chapter.is_published:
            chapter.is_published = False
            chapter.save()
            delete_chapter.delay(chapter.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data={"data": "Нельзя редактировать главу, которая еще не опубликована"})


class UserTeamsWithChapterAccess(APIView):
    def get(self, request, *args, **kwargs):
        in_teams = []
        if self.request.user.is_authenticated:
            in_teams = TeamParticipant.objects.filter(
                Q(user=request.user) &
                (Q(roles__icontains=TeamParticipant.Role.ADMIN) | Q(roles__icontains=TeamParticipant.Role.UPLOADER))
            ).values_list("team_id", "team__name", flat=False)
            if in_teams:
                return Response(
                    data={"in_teams": [{"id": team[0], "name": team[1]} for team in in_teams]},
                    status=status.HTTP_200_OK)
        return Response(
            data={
                "data": "Вы должны состоять в команде и быть администратором или загрузчиком, чтобы загружать главы"},
            status=status.HTTP_400_BAD_REQUEST
        )


class ChapterDetail(generics.RetrieveAPIView):
    serializer_class = ChapterDetailSerializer

    def get_object(self):
        title_slug = self.kwargs.get("title_slug")
        team_slug = self.kwargs.get("team_slug")
        volume = self.kwargs.get("volume")
        number = self.kwargs.get("number")
        # check permissions
        if get_object_or_404(Title, slug=title_slug).age_rating == Title.TitleAgeRating.MATURE:
            if self.request.user.is_anonymous:
                raise NotAuthenticatedException
            elif self.request.user.birth_date + relativedelta(years=18) > datetime.date.today():
                raise NotMatureException
        # get chapter
        return get_object_or_404(
            Chapter.objects.annotate(
                liked_by_user=Exists(
                    ChapterLikes.objects.filter(chapter_id=OuterRef("id"), user_id=self.request.user.id)
                ) if self.request.user.is_authenticated else Value(False),
                images=ArrayAgg(F("images_of_chapter__image"))
            ),
            title__slug=title_slug,
            team__slug=team_slug,
            volume_number=volume,
            chapter_number=number,
            is_published=True
        )


class AllTitleTeamChapters(generics.ListAPIView):
    serializer_class = AllTitleTeamChaptersSerializer
    pagination_class = None

    def get_queryset(self):
        return Chapter.objects.filter(
            title__slug=self.kwargs.get("title_slug"),
            team__slug=self.kwargs.get("team_slug"),
            is_published=True
        ).order_by("-volume_number", "-chapter_number")
