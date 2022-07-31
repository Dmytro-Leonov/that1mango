from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from django.db.models import (
    F, Sum, Subquery, OuterRef, IntegerField, Q, Count, BooleanField, ExpressionWrapper, FloatField
)
from django.db.models.functions import Greatest, Coalesce
from django.shortcuts import get_object_or_404
from .models import List, ListTitle, Subscription, Friend, Notification, Comment, CommentVote
from .serializers import (
    ListSerializer, ListCreateSerializer, SubscriptionSerializer, ListTitleSerializer, ListTitleListSerializer,
    FriendRequestNotificationSerializer, NotificationSerializer, CreateDefaultListsSerializer, CommentListSerializer,
    CommentVoteSerializer, CommentSerializer, CommentUpdateSerializer, FriendSerializer, DeleteNotificationsSerializer
)
from django_filters import rest_framework as filters
from .filters import ListTitleFilter, CommentsFilter
from .tasks import notify_user_of_comment_reply
from .utils import UserDeleteWriteListTitlePermission, NotificationPermission, CommentPermission, \
    UserDeleteWritePermission
from django.apps import apps

Title = apps.get_model(app_label="title", model_name="Title")
TeamParticipant = apps.get_model(app_label="title", model_name="TeamParticipant")
UserTitleRating = apps.get_model(app_label="title", model_name="UserTitleRating")
User = apps.get_model(app_label="users", model_name="User")
MAX_LISTS = 20


class ListCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if List.objects.filter(user=self.request.user).count() >= MAX_LISTS:
            return Response(
                data={"data": f"Вы уже создали максимально допустимое количество списков ({MAX_LISTS})"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            try:
                List.objects.create(
                    user=self.request.user,
                    name=request.data.get("name"),
                    hidden=request.data.get("hidden")
                )
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    data={"name": "Вы уже создали список с таким названием"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListsView(generics.ListAPIView):
    serializer_class = ListSerializer
    pagination_class = None
    lookup_field = "username"

    def get_queryset(self):
        username = self.kwargs.get("username")
        if self.request.user.username == username:
            return List.objects.filter(user__username=username)
        return List.objects.filter(user__username=username, hidden=False)


class ListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView, UserDeleteWritePermission):
    serializer_class = ListCreateSerializer
    permission_classes = [UserDeleteWritePermission]

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get("id")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user_list = get_object_or_404(List, id=pk)
                self.check_object_permissions(self.request, user_list)
                user_list.name = request.data.get("name")
                user_list.hidden = request.data.get("hidden")
                user_list.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(
                    data={"name": "Вы уже создали список с таким названием"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, queryset=None, **kwargs):
        pk = self.kwargs.get("id")
        user_list = get_object_or_404(List, id=pk)
        self.check_object_permissions(self.request, user_list)
        return user_list


class Subscribe(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def post(self, request, *args, **kwargs):
        try:
            title = request.data.get("title")
            team = request.data.get("team")
            if not title and not team or not title and team:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                Subscription.objects.create(
                    user=self.request.user,
                    title_id=title,
                    team_id=team
                )
                return Response(status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Unsubscribe(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def destroy(self, request, *args, **kwargs):
        subscription = Subscription.objects.filter(
            user_id=self.request.user.id,
            title_id=request.data.get("title"),
            team_id=request.data.get("team")
        ).first()
        if subscription:
            subscription.delete()
            return Response(data={"data": "Подписка удалена"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class ListTitleCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListTitleSerializer

    def create(self, request, *args, **kwargs):
        try:
            user_list = request.data.get("list")
            title = request.data.get("title")
            if List.objects.get(id=user_list).user != self.request.user:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            ListTitle.objects.create(
                list_id=user_list,
                title_id=title
            )
            return Response(status=status.HTTP_200_OK)
        except (IntegrityError, List.DoesNotExist):
            return Response(
                data={"data": "Вы уже добавили тайтл в этот список или такого списка не существует"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ListTitleRetrieveDestroy(generics.DestroyAPIView, UserDeleteWriteListTitlePermission):
    permission_classes = [IsAuthenticated, UserDeleteWriteListTitlePermission]

    def destroy(self, request, *args, **kwargs):
        list_id = self.kwargs.get("list_id")
        title_id = self.kwargs.get("title_id")
        list_title = get_object_or_404(ListTitle, list=list_id, title=title_id)
        self.check_object_permissions(self.request, list_title)
        list_title.delete()
        return Response(status=status.HTTP_200_OK)


class ListTitlesList(generics.ListAPIView):
    serializer_class = ListTitleListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ListTitleFilter

    def get_queryset(self):
        list_id = self.kwargs.get("list_id")
        return Title.objects.filter(lists_of_title__list=list_id).annotate(
            total_rating=Coalesce(
                Sum(
                    F("ratings_of_title__amount") * 1.0 * F("ratings_of_title__rating__mark")
                ) / Greatest(Sum("ratings_of_title__amount"), 1), 0,
                output_field=FloatField()
            ),
            added=F("lists_of_title__date_added"),
            user_rating=Coalesce(
                Subquery(
                    UserTitleRating.objects.filter(
                        user=OuterRef("lists_of_title__list__user"), title_id=OuterRef("id")
                    ).values("rating"),
                    output_field=IntegerField()
                ), 0
            )
        )


class UserListsOfTitle(APIView):
    def get(self, request, *args, **kwargs):
        in_user_lists = list(
            ListTitle.objects.filter(
                Q(list__user=self.kwargs.get("user_id")) &
                Q(title=self.kwargs.get("title_id"))
            ).values_list("list", flat=True)
        )
        return Response(data={"in_user_lists": in_user_lists}, status=status.HTTP_200_OK)


class AcceptFriendInvite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        notification_id = self.kwargs.get("notification_id")
        notification = get_object_or_404(Notification, id=notification_id)

        if notification.user.id != user_id or notification.type != Notification.NotificationType.FRIEND_REQUEST \
                or not notification.friend:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user_id != notification.friend.id:
            try:
                with transaction.atomic():
                    Friend.objects.bulk_create(
                        [
                            Friend(user_id=user_id, friend_id=notification.friend.id),
                            Friend(user_id=notification.friend.id, friend_id=user_id)
                        ]
                    )
                    Notification.objects.create(
                        user=notification.friend, friend_id=user_id, type=Notification.NotificationType.FRIEND_ACCEPTED
                    )
                    notification.delete()
                    return Response(status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(
                    data={"data": "Ошибка при добавлении друга"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(data={"data": "Нельзя добавить себя в друзья"}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = FriendSerializer(data=request.data)
        if serializer.is_valid():
            Friend.objects.filter(
                Q(user_id=self.request.user.id) & Q(friend_id=serializer.data.get("friend")) |
                Q(user_id=serializer.data.get("friend")) & Q(friend_id=self.request.user.id)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendRequestNotificationCreate(generics.CreateAPIView):
    serializer_class = FriendRequestNotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        if user_id != self.request.user.id and \
                not Notification.objects.filter(user=self.request.user, friend=user_id).exists():
            Notification.objects.create(
                user_id=user_id, friend=self.request.user, type=Notification.NotificationType.FRIEND_REQUEST
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(
            data={"data": "Этот пользователь уже отправил вам запрос на дружбу, "
                          "вы можете принять ее перейдя в раздел уведомлений"},
            status=status.HTTP_400_BAD_REQUEST
        )


class NotificationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView, NotificationPermission):
    permission_classes = [IsAuthenticated, NotificationPermission]
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("id")
        user_notification = get_object_or_404(Notification, id=pk)
        self.check_object_permissions(self.request, user_notification)
        user_notification.is_read = True
        user_notification.save()
        return Response(status=status.HTTP_200_OK)

    def get_object(self, queryset=None, **kwargs):
        pk = self.kwargs.get("id")
        user_notification = get_object_or_404(Notification, id=pk)
        self.check_object_permissions(self.request, user_notification)
        return user_notification


class CreateDefaultLists(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        try:
            lists = List.objects.bulk_create(
                [
                    List(user=user, name="Читаю", hidden=False),
                    List(user=user, name="Буду читать", hidden=False),
                    List(user=user, name="Прочитано", hidden=False),
                    List(user=user, name="Брошено", hidden=False),
                    List(user=user, name="Любимое", hidden=False),
                ]
            )
            return Response(data=CreateDefaultListsSerializer(lists, many=True).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                data={"name": "Вы уже создали список с таким названием"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CountNotifications(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications_count = Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).count()
        return Response(data={"notifications": notifications_count}, status=status.HTTP_200_OK)


class CommentVoteCreate(generics.CreateAPIView):
    serializer_class = CommentVoteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                CommentVote.objects.create(
                    user_id=self.request.user.id,
                    comment_id=serializer.data.get("comment"),
                    vote=serializer.data.get("vote")
                )
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CommentVoteDestroy(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        try:
            CommentVote.objects.get(comment_id=comment_id, user_id=self.request.user.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CommentVote.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TitleCommentsList(generics.ListAPIView):
    serializer_class = CommentListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CommentsFilter

    def get_queryset(self):
        title = self.kwargs.get("title")
        comments = Comment.objects.filter(title=title, reply_to__isnull=True).annotate(
            count_replies=Count("replies"),
            total_likes=F("likes") - F("dislikes"),
        )
        if self.request.user.is_anonymous:
            return comments
        else:
            return comments.annotate(
                vote=Subquery(
                    CommentVote.objects.filter(
                        user_id=self.request.user.id,
                        comment_id=OuterRef("id")
                    ).values("vote")
                ),
                is_author=ExpressionWrapper(Q(user_id=self.request.user.id), output_field=BooleanField())
            )


class TitleCommentCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            reply_to_id = serializer.data.get("reply_to")
            title_id = serializer.data.get("title")
            user_id = self.request.user.id
            with transaction.atomic():
                try:
                    comment = Comment.objects.create(
                        user_id=user_id,
                        title_id=title_id,
                        comment=serializer.data.get("comment"),
                        reply_to_id=reply_to_id,
                        is_deleted=serializer.data.get("is_deleted")
                    )
                    if reply_to_id:
                        notify_user_of_comment_reply.delay(reply_to_id, user_id)
                    return Response(data=self.serializer_class(comment).data, status=status.HTTP_201_CREATED)
                except IntegrityError:
                    return Response(data={"data": "Ошибка оценки комментария"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TitleCommentUpdate(APIView, CommentPermission):
    permission_classes = [IsAuthenticated, CommentPermission]
    serializer_class = CommentUpdateSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            comment = get_object_or_404(Comment, id=serializer.data.get("id"))
            self.check_object_permissions(self.request, comment)
            if comment.is_deleted:
                return Response(
                    data={"data": "Нельзя редактировать удаленные комментарии"}, status=status.HTTP_400_BAD_REQUEST
                )
            if serializer.data.get("is_deleted"):
                comment.comment = ""
                comment.is_deleted = serializer.data.get("is_deleted")
            else:
                comment.comment = serializer.data.get("comment")
                comment.is_deleted = serializer.data.get("is_deleted")
            comment.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TitleCommentsRepliesList(generics.ListAPIView):
    serializer_class = CommentListSerializer
    filterset_class = None

    def get_queryset(self):
        comment_id = self.kwargs.get("comment_id")
        comments = Comment.objects.filter(reply_to_id=comment_id).annotate(
            count_replies=Count("replies"),
            total_likes=F("likes") - F("dislikes")
        )
        if self.request.user.is_anonymous:
            return comments
        else:
            return comments.annotate(
                vote=Subquery(
                    CommentVote.objects.filter(
                        user_id=self.request.user.id,
                        comment_id=OuterRef("id"),
                    ).values("vote")
                ),
                is_author=ExpressionWrapper(Q(user_id=self.request.user.id), output_field=BooleanField())
            )


class AcceptTeamInvite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        notification_id = self.kwargs.get("notification_id")
        notification = get_object_or_404(Notification, id=notification_id)

        if notification.user.id != user_id or notification.type != Notification.NotificationType.JOIN_TEAM_REQUEST \
                or not notification.team:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            TeamParticipant.objects.create(user_id=user_id, team_id=notification.team.id)
            notification.delete()
            return Response(status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                data={"data": "Вы уже являетеся учасником этой команды или ее не существует"},
                status=status.HTTP_400_BAD_REQUEST
            )


class NotificationList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = None

    def get_queryset(self):
        return Notification.objects.filter(user_id=self.request.user).order_by("-id")


class ReadAllNotifications(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Notification.objects.filter(user=self.request.user, is_read=False).update(is_read=True)
        return Response(status=status.HTTP_200_OK)


class DeleteNotifications(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteNotificationsSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Notification.objects.filter(user=self.request.user, is_read=serializer.data.get("is_read")).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
