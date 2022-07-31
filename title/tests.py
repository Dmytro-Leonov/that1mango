from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from django.apps import apps

from .models import (
    Rating, ReleaseFormat, Publisher, Person, Keyword, Title, Chapter, UserTitleRating, Team, ChapterLikes
)


# Create your tests here.
class UserAccountTests(APITestCase):

    # Check default superuser data
    def test_component_names(self):
        # Create user
        testuser = get_user_model().objects.create_superuser(
            email="testuser1@user.com",
            username="testusername",
            password="usernamepass",
        )
        client1 = APIClient()
        refresh = RefreshToken.for_user(testuser)
        client1.credentials(HTTP_AUTHORIZATION='JWT ' + str(refresh.access_token))

        # url7 = reverse("social:userCreateDefaultLists")
        # response9 = client1.post(url7)
        # self.assertEqual(response9.status_code, status.HTTP_201_CREATED)

        # Create user2
        testuser2 = get_user_model().objects.create_superuser(username='testusername2', email='testuser2@user.com',
                                                              password='testuserpassword2')
        client2 = APIClient()
        refresh = RefreshToken.for_user(testuser2)
        client2.credentials(HTTP_AUTHORIZATION='JWT ' + str(refresh.access_token))

        # Create format of title
        releaseformat = ReleaseFormat.objects.create(
            name="testrel",
            slug="sulgtest"
        )
        self.assertEqual(str(releaseformat), "testrel")

        # Create rate
        testrating = Rating.objects.create(
            mark=5,
        )
        self.assertEqual(str(testrating), "Оценка 5")

        # Create publisher
        publisher = Publisher.objects.create(
            name="TestPublisher",
            slug="testpublisherslug",
            alternative_names=r"{altname}"
        )
        self.assertEqual(str(publisher), "TestPublisher")

        # Create person
        testperson = Person.objects.create(
            name="TestPerson",
            alternative_names=r"{altname}"
        )
        self.assertEqual(str(testperson), "TestPerson")

        # Create tag
        testkeyword = Keyword.objects.create(
            name="Catgirl",
            slug="koshkodevki"
        )
        self.assertEqual(str(testkeyword), "Catgirl")

        # Create title
        testtitle = Title.objects.create(
            name="Кошачий рай",
            slug="koshachii-rai",
            english_name="Nekopara",
            alternative_names=["Cats Paradise"],
            description="What's NEKOPARA? Why, it's a cat paradise!",
            release_year=2020,
            poster="//",
            chapter_count=1,
            licensed=True,
        )
        # Add tag to title
        keyword1 = testtitle.keywords.create(name="Catgirls", slug="koshkodevochki")
        self.assertEqual(str(testtitle), "Кошачий рай")

        # Check filter of title
        url = reverse("title:titleList")
        response = Client().get(url, dict(keyword="koshkodevochki", name="Nekopara"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print("DATA STARTS\n",response.data, "DATA ENDS\n")
        self.assertEqual(response.data['count'], 1)

        # Check filter with wrong keyword
        response1 = Client().get(url, dict(keyword="lgbt", name="Nekopara"))
        self.assertEqual(response1.data['keyword'][0],
                         'Select a valid choice. lgbt is not one of the available choices.')

        # Check filter with wrong name
        response2 = Client().get(url, dict(keyword="koshkodevochki", name="Jojo"))
        self.assertEqual(response2.data["count"], 0)

        # Check Title page
        url2 = reverse("title:titleDetail", kwargs={"slug": "koshachii-rai"})
        response3 = Client().get(url2)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

        # Check Title page but slug is wrong
        url3 = reverse("title:titleDetail", kwargs={"slug": "wrong-slug"})
        response4 = Client().get(url3)
        self.assertEqual(response4.status_code, status.HTTP_404_NOT_FOUND)

        # Add rate
        User_Title_Rating = UserTitleRating.objects.create(
            user=testuser,
            title=testtitle,
            rating=testrating
        )
        self.assertEqual(str(User_Title_Rating), "testusername - Кошачий рай: Оценка 5")

        # Create translator tem
        testteam = Team.objects.create(
            name="Команда переводчиков",
            slug="komanda_perevodchikov"
        )
        self.assertEqual(str(testteam), "Команда переводчиков")

        # Add chapter
        testchapter = Chapter.objects.create(
            title=testtitle,
            name="Meat huh. Must be meat.",
            volume_number=1,
            chapter_number=1.1,
            team=testteam,
        )
        self.assertEqual(str(testchapter), "Кошачий рай - Том 1 Глава 1.1")

        # Add like to chapter
        Chapter_Likes = ChapterLikes.objects.create(
            user=testuser,
            chapter=testchapter
        )
        self.assertEqual(str(Chapter_Likes), "testusername liked Meat huh. Must be meat.")

        # Create comment to title
        Comment = apps.get_model(app_label="social", model_name="Comment")
        testcomment = Comment.objects.create(
            title=testtitle,
            user=testuser,
            comment="Nekopara is the best"
        )
        self.assertEqual(str(testcomment), "1: Nekopara is the best")

        # Create list of titles for user
        urlListCreate = reverse("social:userListCreate")
        responseList = client1.post(urlListCreate, {"name": "Best time travelling mangas", "hidden": "True"},
                                    format="json")
        self.assertEqual(responseList.status_code, status.HTTP_201_CREATED)

        # Test model of List
        List = apps.get_model(app_label="social", model_name="List")
        testList = List.objects.create(
            user=testuser2,
            name="Best junji ito titles",
        )
        self.assertEqual(str(testList), "Best junji ito titles")

        # Add title to list
        urlAddTitle = reverse("social:listTitleCreate")
        responseAdd = client1.post(urlAddTitle, {"list": "1", "title": "1"}, format="json")
        self.assertEqual(responseAdd.status_code, status.HTTP_200_OK)

        # Add title to list of other user
        with transaction.atomic():
            responseAddToOther = client2.post(urlAddTitle, {"list": "1", "title": "1"}, format="json")
            self.assertEqual(responseAddToOther.status_code, status.HTTP_400_BAD_REQUEST)

        # Add same title to list
        with transaction.atomic():
            responseSameAdd = client1.post(urlAddTitle, {"list": "1", "title": "1"}, format="json")
            self.assertEqual(responseSameAdd.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(responseSameAdd.data["data"],
                             "Вы уже добавили тайтл в этот список или такого списка не существует")

        # Test Lists with same name
        with transaction.atomic():
            responseList = client1.post(urlListCreate, {"name": "Best time travelling mangas", "hidden": "True"},
                                        format="json")
            self.assertEqual(responseList.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(responseList.data["name"], "Вы уже создали список с таким названием")

        # Tet serializer error (empty name of new List)
        with transaction.atomic():
            responseError = client1.post(urlListCreate, {"hidden": "True"}, format="json")
            self.assertEqual(responseError.status_code, status.HTTP_400_BAD_REQUEST)

        for i in range(2, 21):
            testlist2 = List.objects.create(user=testuser, name="list" + str(i))

        # Test cap of 20 lists
        with transaction.atomic():
            urlListMaxed = reverse("social:userListCreate")
            responseMaxed = client1.post(urlListMaxed, {"name": "Best time travelling mangas", "hidden": "False"},
                                         format="json")
            self.assertEqual(responseMaxed.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(responseMaxed.data["data"],
                             "Вы уже создали максимально допустимое количество списков (20)")

        # Get list of title
        url4 = reverse("social:listTitlesList", kwargs={"list_id": 1})
        response5 = Client().get(url4)
        self.assertEqual(response5.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response5.data['results']), 1)
        self.assertEqual(response5.data['results'][0]['name'], 'Кошачий рай')

        # Test comment
        url5 = reverse("social:titleComments", kwargs={"title": 1})
        response6 = Client().get(url5)
        self.assertEqual(response6.status_code, status.HTTP_200_OK)
        self.assertEqual(response6.data['count'], 1)
        self.assertEqual(response6.data['results'][0]['comment'], 'Nekopara is the best')

        # Create reply comment
        url6 = reverse("social:titleCommentCreate")
        c_data = {
            "id": "2",
            "reply_to": "1",
            "title": "1",
            "comment": "Agree",
            "creation_date": "2022-07-02T17:52:15.778779Z",
            "is_deleted": "false"
        }
        response7 = client2.post(url6, c_data, format="json")
        self.assertEqual(response7.status_code, status.HTTP_201_CREATED)

        # Create reply comment but source doesn't exists
        c_wrong_data = {
            "id": "2",
            "reply_to": "100",
            "title": "1",
            "comment": "Agree",
            "creation_date": "2022-07-02T17:52:15.778779Z",
            "is_deleted": "false"
        }
        with transaction.atomic():
            response8 = client2.post(url6, c_wrong_data, format="json")
            self.assertEqual(response8.status_code, status.HTTP_400_BAD_REQUEST)

        # Trying to edit list
        urlEdit = reverse("social:userList", kwargs={"id": 1})
        responseEdit = client1.put(urlEdit, {"name": "Other name of list", "hidden": "True"}, format="json")
        self.assertEqual(responseEdit.status_code, status.HTTP_200_OK)

        # Change list on the same name of other list
        with transaction.atomic():
            responseChange = client1.put(urlEdit, {"name": "list4", "hidden": "True"}, format="json")
            self.assertEqual(responseChange.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(responseChange.data["name"], "Вы уже создали список с таким названием")

        # Change list data with wrong input data (name is empty)
        with transaction.atomic():
            responseError = client1.put(urlEdit, {"hidden": "True"}, format="json")
            self.assertEqual(responseError.status_code, status.HTTP_400_BAD_REQUEST)

        # Trying to delete list of same and other user
        url7 = reverse("social:userList", kwargs={"id": 1})
        response9 = client2.delete(url7)
        self.assertEqual(response9.status_code, status.HTTP_403_FORBIDDEN)

        response10 = client1.delete(url7)
        self.assertEqual(response10.status_code, status.HTTP_204_NO_CONTENT)

        # Get Lists of 1 user to 1 user
        url8 = reverse("social:userLists", kwargs={"username": "testusername"})
        response11 = client1.get(url8)
        self.assertEqual(response11.status_code, status.HTTP_200_OK)

        # Get Lists of 1 user to 2 user
        response12 = client2.get(url8)
        self.assertEqual(response12.status_code, status.HTTP_200_OK)

        # Test subscribe
        url9 = reverse("social:subscribe")
        response13 = client1.post(url9, {"title": "1", "team": "1"})
        self.assertEqual(response13.status_code, status.HTTP_200_OK)

        # Test subscribe but only comand(without title)
        with transaction.atomic():
            response14 = client1.post(url9, {"team": "1"})
            self.assertEqual(response14.status_code, status.HTTP_400_BAD_REQUEST)

        # #Test subscribe but integrity error
        # with transaction.atomic():
        #     response15 = client1.post(url9, {"title":"10000","team":"10000"}, format = "json")
        #     self.assertEqual(response15.status_code, status.HTTP_400_BAD_REQUEST)
        #     self.assertEqual(response15.data["data"], "Error")

        # Test unsubscribe but such subscribe not found
        url10 = reverse("social:unsubscribe")
        response16 = client1.delete(url10, {"title": "2", "team": "1"})
        self.assertEqual(response16.status_code, status.HTTP_404_NOT_FOUND)

        # Test unsubscribe
        response17 = client1.delete(url10, {"title": "1", "team": "1"})
        self.assertEqual(response17.status_code, status.HTTP_200_OK)
        self.assertEqual(response17.data["data"], "Подписка удалена")

        client2.post(urlAddTitle, {"list": "2", "title": "1"}, format="json")

        # Test TitleDestroy but it not found
        urlDestroyTitle404 = reverse("social:listTitleRetrieveDestroyAPIView", kwargs={"list_id": 2, "title_id": 50})
        response404DestroyTitle = client2.delete(urlDestroyTitle404)
        self.assertEqual(response404DestroyTitle.status_code, status.HTTP_404_NOT_FOUND)

        # # Test TitleDestroy but serializer error
        # urlError = reverse("social:listTitleRetrieveDestroyAPIView", kwargs={"list_id": 50, "title_id": 50})
        # responseError = client2.delete(urlError)
        # self.assertEqual(responseError.status_code, status.HTTP_400_BAD_REQUEST)

        # Test TitleDestroy in List
        urlDestroyTitleInList = reverse("social:listTitleRetrieveDestroyAPIView", kwargs={"list_id": 2, "title_id": 1})
        responseDestroyTitleInList = client2.delete(urlDestroyTitleInList)
        self.assertEqual(responseDestroyTitleInList.status_code, status.HTTP_200_OK)

        f = client2.post(urlAddTitle, {"list": "2", "title": "1"}, format="json")

        # Test something I already don't know
        url11 = reverse("social:userListsOfTitle", kwargs={"user_id": 4, "title_id": 1})
        response18 = client2.get(url11)
        self.assertEqual(response18.status_code, status.HTTP_200_OK)
        self.assertEqual(response18.data["in_user_lists"][0], 2)

        # Test Friend Requests but to yourself
        with transaction.atomic():
            url12 = reverse("social:FriendNotificationCreate")
            response19 = client1.post(url12, {"user": 3}, format="json")
            self.assertEqual(response19.status_code, status.HTTP_400_BAD_REQUEST)

        # Test Friend Requests
        with transaction.atomic():
            response20 = client1.post(url12, {"user": 4}, format="json")
            self.assertEqual(response20.status_code, status.HTTP_201_CREATED)

        # #Test Friend Requests but Integrity Error
        # with transaction.atomic():
        #     response20 = client1.post(url12, {"user":1}, format="json")
        #     self.assertEqual(response20.status_code, status.HTTP_400_BAD_REQUEST)

        # Get all notifications of one user
        url13 = reverse("social:notificationCreate")
        response21 = client2.get(url13)
        self.assertEqual(response21.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response21.data), 1)

        # Update status of notification
        url14 = reverse("social:notificationRetrieveUpdateDestroyView", kwargs={"id": 1})
        response22 = client2.patch(url14, {"is_read": True}, format="json")
        self.assertEqual(response22.status_code, status.HTTP_200_OK)

        # Accept friend invite
        url15 = reverse("social:friendCreateDestroy", kwargs={"notification_id": 1})
        response23 = client2.post(url15, format="json")
        self.assertEqual(response23.status_code, status.HTTP_200_OK)

        # Accept friend invite but notification is not valid
        url16 = reverse("social:friendCreateDestroy", kwargs={"notification_id": 2})
        response24 = client2.post(url16, format="json")
        self.assertEqual(response24.status_code, status.HTTP_400_BAD_REQUEST)

        # Trying to add yourself to friends
        url17 = reverse("social:friendCreateDestroy", kwargs={"notification_id": 3})
        Notification = apps.get_model(app_label="social", model_name="Notification")
        Notification.objects.create(
            user=testuser2,
            friend=testuser2,
            type=3,
            is_read=False
        )
        response25 = client2.post(url17, format="json")
        self.assertEqual(response25.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response25.data["data"], "Нельзя добавить себя в друзья")

        # Remove friend from friendlist but data is not valid (empty)
        with transaction.atomic():
            url18 = reverse("social:friendCreateDestroy")
            response26 = client2.delete(url18, format="json")
            self.assertEqual(response26.status_code, status.HTTP_400_BAD_REQUEST)

        # Remove friend from friendlist
        response27 = client2.delete(url18, {"friend": 3}, format="json")
        self.assertEqual(response27.status_code, status.HTTP_204_NO_CONTENT)
