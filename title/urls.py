from django.urls import path, register_converter
from .converters import FloatConverter
from .views import (
    TitleDetails, TitleList, LikeChapter, RateTitle, RateTitleGet, RateTitleDestroy, ChapterListForTeam,
    GetAllFilteringValues, PersonCreateView, PersonDetailView, PersonTitlesGetView, PublisherCreateView, TeamCreateView,
    PublisherDetailView, PublisherTitlesGetView, TeamDetailView, TeamTitlesGetView, RandomTitleView, NewTitles,
    NewChapters, DeleteTeamPicture, DeletePersonPicture, DeletePublisherPicture, InviteToTeam, TitleSearchView,
    TeamParticipantUpdateDestroy, PersonSearchView, PublisherSearchView, TeamSearchView, PopularNowTitles,
    UploadChapter, UpdateChapter, DeleteChapter, UserTeamsWithChapterAccess, ChapterDetail, AllTitleTeamChapters,

)

app_name = "title"

register_converter(FloatConverter, "float")

urlpatterns = [
    # main page
    path("new-titles/", NewTitles.as_view(), name="latestTitles"),
    path("new-chapters/", NewChapters.as_view(), name="latestChapters"),
    path("popular-now-titles/", PopularNowTitles.as_view(), name="popularTitles"),
    # person
    path("person/", PersonCreateView.as_view(), name="personCreate"),
    path("person/<int:person_id>/", PersonDetailView.as_view(), name="personRetrieveUpdateDestroy"),
    path("person/delete-person-picture/<int:person_id>/", DeletePersonPicture.as_view(), name="personDestroyPicture"),
    path("person/titles/<int:person_id>/", PersonTitlesGetView.as_view(), name="personTitlesGet"),
    # publisher
    path("publisher/", PublisherCreateView.as_view(), name="publisherCreate"),
    path("publisher/<slug:slug>/", PublisherDetailView.as_view(), name="publisherRetrieveUpdateDestroy"),
    path(
        "publisher/delete-publisher-picture/<int:publisher_id>/",
        DeletePublisherPicture.as_view(),
        name="publisherDestroyPicture"
    ),
    path("publisher/titles/<slug:slug>/", PublisherTitlesGetView.as_view(), name="publisherTitlesGet"),
    # team
    path("team/", TeamCreateView.as_view(), name="teamCreate"),
    path("team/invite/", InviteToTeam.as_view(), name="teamInvite"),
    path("team/participant/", TeamParticipantUpdateDestroy.as_view(), name="teamParticipantUpdateDestroy"),
    path("team/<slug:slug>/", TeamDetailView.as_view(), name="teamRetrieveUpdateDestroy"),
    path("team/delete-team-picture/<int:team_id>/", DeleteTeamPicture.as_view(), name="teamDestroyPicture"),
    path("team/titles/<slug:slug>/", TeamTitlesGetView.as_view(), name="teamTitlesGet"),
    # searches
    path("title/search/<str:name>/", TitleSearchView.as_view(), name="titleSearch"),
    path("person/search/<str:name>/", PersonSearchView.as_view(), name="personSearch"),
    path("publisher/search/<str:name>/", PublisherSearchView.as_view(), name="publisherSearch"),
    path("team/search/<str:name>/", TeamSearchView.as_view(), name="teamSearch"),
    # titles
    path("filters/", GetAllFilteringValues.as_view(), name="allFilters"),
    path("random/", RandomTitleView.as_view(), name="randomTitle"),
    path("", TitleList.as_view(), name="titleList"),
    path("<slug:slug>/", TitleDetails.as_view(), name="titleDetail"),
    path("title/rate/", RateTitle.as_view(), name="rateTitle"),
    path("title/get-rate/", RateTitleGet.as_view(), name="rateTitleGet"),
    path("title/delete-rate/", RateTitleDestroy.as_view(), name="rateTitleDestroy"),
    # chapters
    path("chapter/like/", LikeChapter.as_view(), name="likeChapter"),
    path("chapters/<int:title_id>/<int:team_id>/", ChapterListForTeam.as_view(), name="rateTitleDestroy"),
    path("chapter/upload/", UploadChapter.as_view(), name="chapterUpload"),
    path("chapter/update/<int:chapter_id>/", UpdateChapter.as_view(), name="chapterUpdate"),
    path("chapter/delete/<int:chapter_id>/", DeleteChapter.as_view(), name="chapterDelete"),
    path("chapter/teams-with-chapter-access/", UserTeamsWithChapterAccess.as_view(), name="userTeamsWithChapterAccess"),
    path(
        r"chapter/<slug:title_slug>/<slug:team_slug>/<int:volume>/<float:number>/",
        ChapterDetail.as_view(),
        name="chapterDetail"
    ),
    path("chapters/<slug:title_slug>/<slug:team_slug>/", AllTitleTeamChapters.as_view(), name="allTitleTeamChapters"),
]
