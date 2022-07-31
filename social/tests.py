from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Friend


# Test user views
class ModelTests(APITestCase):

    def test_userDetail_GET(self):
        db = get_user_model()

        user1 = db.objects.create_superuser(
            email="testuser1@user.com",
            username="testusername1",
            password="testuserpassword1",
        )

        user2 = db.objects.create_superuser(
            email="testuser2@user.com",
            username="testusername2",
            password="testuserpassword2",
        )

        friendship = Friend.objects.create(
            user=user1,
            friend=user2
        )
        self.assertEqual(str(friendship), "testusername1 -> testusername2")
