from django.urls import path
from .views import (
    UserListsView, ListRetrieveUpdateDestroyView, ListCreateView, Subscribe, Unsubscribe, ListTitleCreate,
    ListTitleRetrieveDestroy, ListTitlesList, AcceptFriendInvite, FriendRequestNotificationCreate,
    NotificationRetrieveUpdateDestroyView, CreateDefaultLists, UserListsOfTitle, CountNotifications,
    TitleCommentsList, CommentVoteCreate, CommentVoteDestroy, TitleCommentCreate, TitleCommentUpdate,
    TitleCommentsRepliesList, AcceptTeamInvite, RemoveFriendView, NotificationList, ReadAllNotifications,
    DeleteNotifications
)

app_name = "social"

urlpatterns = [
    path("lists/list/", ListCreateView.as_view(), name="userListCreate"),
    path("lists/list/<int:id>/", ListRetrieveUpdateDestroyView.as_view(), name="userList"),
    path("lists/lists/<str:username>/", UserListsView.as_view(), name="userLists"),
    path("lists/create-default/", CreateDefaultLists.as_view(), name="userCreateDefaultLists"),
    path(
        "lists/title-in-user-lists/<int:user_id>/<int:title_id>/", UserListsOfTitle.as_view(), name="userListsOfTitle"
    ),

    path("create-list-title/", ListTitleCreate.as_view(), name="listTitleCreate"),
    path(
        "list-title/<int:list_id>/<int:title_id>/",
        ListTitleRetrieveDestroy.as_view(),
        name="listTitleRetrieveDestroyAPIView"
    ),
    path("list-titles/<int:list_id>/", ListTitlesList.as_view(), name="listTitlesList"),

    path("subscribe/", Subscribe.as_view(), name="subscribe"),
    path("unsubscribe/", Unsubscribe.as_view(), name="unsubscribe"),

    path("accept-friend-invite/<int:notification_id>/", AcceptFriendInvite.as_view(), name="friendCreateDestroy"),
    path("accept-team-invite/<int:notification_id>/", AcceptTeamInvite.as_view(), name="userAcceptTeamInvite"),
    path("remove-friend/", RemoveFriendView.as_view(), name="friendCreateDestroy"),
    path("friend-request/", FriendRequestNotificationCreate.as_view(), name="FriendNotificationCreate"),
    path("notifications/", NotificationList.as_view(), name="notificationCreate"),
    path(
        "notification/<int:id>/",
        NotificationRetrieveUpdateDestroyView.as_view(),
        name="notificationRetrieveUpdateDestroyView"
    ),
    path("count-notifications/", CountNotifications.as_view(), name="userCountNotifications"),
    path("notifications/read-all/", ReadAllNotifications.as_view(), name="notificationsReadAll"),
    path("notifications/delete/", DeleteNotifications.as_view(), name="notificationsDeleteAll"),

    path("comments/", TitleCommentCreate.as_view(), name="titleCommentCreate"),
    path("comments/<int:title>/", TitleCommentsList.as_view(), name="titleComments"),
    path("comments/replies/<int:comment_id>/", TitleCommentsRepliesList.as_view(), name="titleCommentsReply"),
    path("comments/update/", TitleCommentUpdate.as_view(), name="titleCommentsUpdate"),
    path("comments/vote/", CommentVoteCreate.as_view(), name="titleCommentsVote"),
    path("comments/vote-delete/<int:comment_id>/", CommentVoteDestroy.as_view(), name="titleCommentsDeleteVote"),
]
