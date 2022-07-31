import sys
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db import transaction
from .models import User


# create logged client
class UserAccountTests(APITestCase):
    # Check common data
    def test_total(self):
        self.assertEqual("test" in sys.argv, True)

    # Check default superuser data
    def test_new_superuser(self):
        db = get_user_model()
        super_user1 = db.objects.create_superuser(
            email="testsuperuser1@user.com",
            username="testname1",
            password="testpassword1",
        )

        self.assertEqual(super_user1.email, "testsuperuser1@user.com")
        self.assertEqual(super_user1.username, "testname1")
        self.assertTrue(super_user1.is_staff)
        self.assertTrue(super_user1.is_superuser)
        self.assertTrue(super_user1.is_active)
        self.assertEqual(str(super_user1), "testname1")

        # username must be unique
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                db.objects.create_superuser(
                    email="othertestsuperuser1@user.com",
                    username="testname1",
                    password="othertestpassword1",
                )

        # email must be unique
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                db.objects.create_superuser(
                    email="testsuperuser1@user.com",
                    username="othertestname1",
                    password="othertestpassword1",
                )

        # Staff must be true
        with self.assertRaises(ValueError):
            db.objects.create_superuser(
                email="testsuperuser2@user.com",
                username="testname2",
                password="testpassword2",
                is_staff=False,
            )

        # Superuser must be true
        with self.assertRaises(ValueError):
            db.objects.create_superuser(
                email="testsuperuser3@user.com",
                username="testname3",
                password="testpassword3",
                is_superuser=False,
            )

        # email mustn't be blank
        with self.assertRaises(ValueError):
            db.objects.create_superuser(
                email="", username="testname4", password="testpassword4"
            )

    # Check default user data
    def test_new_user(self):
        db = get_user_model()
        user1 = db.objects.create_user(
            email="testuser1@user.com",
            username="testusername1",
            password="testuserpassword1",
        )
        self.assertEqual(user1.email, "testuser1@user.com")
        self.assertEqual(user1.username, "testusername1")
        self.assertFalse(user1.is_staff)
        self.assertFalse(user1.is_superuser)
        self.assertFalse(user1.is_active)
        self.assertEqual(str(user1), "testusername1")

        # email mustn't be blank
        with self.assertRaises(ValueError):
            db.objects.create_user(
                email="", username="testusername2", password="testuserpassword2"
            )

    # Check permissions
    def test_permissions(self):
        db = get_user_model()
        user1 = db.objects.create_user(
            email="testuser1@user.com",
            username="testusername1",
            password="testuserpassword1",
        )
        self.assertEqual(user1.email, "testuser1@user.com")
        self.assertEqual(user1.username, "testusername1")
        self.assertFalse(user1.is_staff)
        self.assertFalse(user1.is_superuser)
        self.assertFalse(user1.is_active)
        self.assertEqual(str(user1), "testusername1")

        # email mustn't be blank
        with self.assertRaises(ValueError):
            db.objects.create_user(
                email="", username="testusername2", password="testuserpassword2"
            )


# ==================Comment below Register User, but everytime sends a letter of confirmation to email=================#
class UserTests(APITestCase):
    # User Register
    # def test_UserCreate(self):
    #         url = reverse('users:createUser')
    #         data = {
    #             "email":"newuser1@.com",
    #             "username":"newusername1",
    #             "password":"newpass1"
    #             }
    #         response = self.client.post(url, data, format='json')
    #         self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    # User Register BadRequest
    def test_UserBadReq(self):
        url = reverse('users:createUser')
        data = {
            "email": "bademail",
            "username": "newusername2",
            "password": "newpass2"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Validation tests
    def test_validation(self):
        db = get_user_model()
        url = reverse('users:createUser')

        user1 = db.objects.create_user(
            email="testuser1@user.com",
            username="testusername1",
            password="testuserpassword1",
        )

        # Test user with username that already exists
        username_exists = {
            "email": "testuser2@user.com",
            "username": "testusername1",
            "password": "testuserpassword2"
        }
        response = self.client.post(url, username_exists, format='json')
        self.assertEqual(response.data["username"][0], "Это имя пользователя уже занято")

        # Test user with email that already exists
        email_exists = {
            "email": "testuser1@user.com",
            "username": "testusername2",
            "password": "testuserpassword2"
        }
        response = self.client.post(url, email_exists, format='json')
        self.assertEqual(response.data["email"][0], "Этот email уже зарегестрирован")

        # Test user with too short pssword
        short_pass = {
            "email": "testuser1@user.com",
            "username": "testusername2",
            "password": "a"
        }
        response = self.client.post(url, short_pass, format='json')
        self.assertEqual(response.data["password"][0], "Пароль должен быть минимум 8 символов")

        # Test user with too long pssword
        long_pass = {
            "email": "testuser1@user.com",
            "username": "testusername2",
            "password": "What's NEKOPARA? Why, it's a cat paradise!"
        }
        response = self.client.post(url, long_pass, format='json')
        self.assertEqual(response.data["password"][0], "Пароль должен быть меньше 25 символов")

    # Test user views


class ViewTests(APITestCase):

    def test_userDetail_GET(self):
        db = get_user_model()
        client1 = Client()

        user1 = db.objects.create_user(
            email="testuser1@user.com",
            username="testusername1",
            password="testuserpassword1",
        )

        # Check info with right person id
        # url1 = reverse('users:detailRetrieveUpdateDestroy', kwargs={'id': user1.id})
        # response1 = client1.get(url1)
        # self.assertEqual(response1.status_code,status.HTTP_200_OK)

        # Get info with wrong person id
        # url2 = reverse('users:detailRetrieveUpdateDestroy', kwargs={'id': user1.id+1})
        # response2 = client1.get(url2, format='json')
        # self.assertEqual(response2.status_code,status.HTTP_404_NOT_FOUND)

        # Get info with wrong person id
        url2 = reverse('users:detailRetrieveUpdateDestroy', kwargs={'id': user1.id + 1})
        response2 = client1.get(url2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_with_username_or_mail(self):
        db = get_user_model()
        client = Client()

        user1 = db.objects.create_superuser(
            email="testuser1@user.com",
            username="testusername1",
            password="testuserpassword1",
        )

        user2 = db.objects.create_user(
            email="testmail@testmail.tm",
            username="testusername2",
            password="testuserpassword2",
        )

        # Check login by email
        response1 = client.post(
            "/api/users/login/",
            dict(username="testuser1@user.com", password="testuserpassword1"),
            format='json',
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Check login by username
        response2 = client.post(
            "/api/users/login/",
            dict(username="testusername1", password="testuserpassword1"),
            format='json',
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Check user with inactive email
        response4 = client.post(
            "/api/users/login/",
            dict(username="testmail@testmail.tm", password="testuserpassword2"),
            format='json',
        )
        self.assertEqual(response4.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_changing(self):
        user = User.objects.create_superuser(username='testusername1', email='testuser1@user.com',
                                             password='testuserpassword1')
        client1 = APIClient()
        refresh = RefreshToken.for_user(user)
        client1.credentials(HTTP_AUTHORIZATION='JWT ' + str(refresh.access_token))

        # Change password but old_password is wrong
        response1 = client1.patch(
            reverse('users:changePassword'),
            dict(old_password="wrongpassword", new_password="newuserpassword1"),
            format='json',
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # Change password but new password is too short
        response2 = client1.patch(
            reverse('users:changePassword'),
            dict(old_password="testuserpassword1", new_password="a"),
            format='json',
        )
        self.assertEqual(response2.data["new_password"][0], "Пароль должен быть минимум 8 символов")

        # Reset password but new password is too long
        response3 = client1.patch(
            reverse('users:changePassword'),
            dict(old_password="testuserpassword1", new_password="What's NEKOPARA? Why, it's a cat paradise!"),
            format='json',
        )
        self.assertEqual(response3.data["new_password"][0], "Пароль должен быть меньше 25 символов")

        # Change password
        response4 = client1.patch(
            reverse('users:changePassword'),
            dict(old_password="testuserpassword1", new_password="newuserpassword1"),
            format='json',
        )
        self.assertEqual(response4.status_code, status.HTTP_200_OK)

    # Test register and mail activating
    # def test_mail_verification(self):
    #     client = Client()

    #     url = reverse('users:createUser')
    #     data = {
    #         "email":"testuser@user.com",
    #         "username":"newusername1",
    #         "password":"newpass1"
    #         }
    #     response = self.client.post(url, data, format='json')
    #     time.sleep(30)
    #     email_content = django.core.mail.outbox[0].body
    #     id, token = email_content.split("\n")[1].split("?id=")[1].split("&token=")

    #     # Verify email but token is invalid
    #     wrong_token = {
    #         "user_id": id,
    #         "token": token + "wrong",
    #         }
    #     response1 = client.post(
    #         reverse('users:verifyRegistration'),
    #         wrong_token,
    #         format='json'
    #     )
    #     self.assertEqual(response1.status_code, status.HTTP_401_UNAUTHORIZED)

    #     #Verify email but user is not exists
    #     wrong_user = {
    #         "user_id": "NTM",
    #         "token": token,
    #         }
    #     response2 = client.post(
    #         reverse('users:verifyRegistration'),
    #         wrong_user,
    #         format='json'
    #     )
    #     self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    #     #Verify email
    #     data = {
    #         "user_id": id,
    #         "token": token,
    #         }
    #     response3 = client.post(
    #         reverse('users:verifyRegistration'),
    #         data,
    #         format='json'
    #     )
    #     self.assertEqual(response3.status_code, status.HTTP_200_OK)

    #     #Verify email but it is already verified
    #     response4 = client.post(
    #         reverse('users:verifyRegistration'),
    #         data,
    #         format='json'
    #     )
    #     self.assertEqual(response4.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_password_reset(self):
    #     client = Client()
    #     db = get_user_model()

    #     db.objects.create_superuser(
    #         email="testuser1@user.com",
    #         username="testusername1",
    #         password="testuserpassword1",
    #     )
    #     url = reverse('users:sendResetPasswordEmail')

    # Wrong mail to reset password
    # wrong_data = { "email":"wronguser@user.com" }
    # response1 = self.client.post(url, wrong_data, format='json')
    # self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    # Send mail to reset password test
    # data = { "email":"testuser1@user.com" }
    # response2 = self.client.post(url, data, format='json')
    # email_content = django.core.mail.outbox[0].body
    # id, token = email_content.split("\n")[1].split("?id=")[1].split("&token=")
    # self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    # #Reset password
    # url = reverse('users:resetPassword')
    # data = {
    #     "user_id": id,
    #     "token": token,
    #     "new_password": "rtyrtyrty"
    #     }
    # response3 = client.post(url, data, format='json')
    # self.assertEqual(response3.status_code, status.HTTP_200_OK)

    # #Reset password but token is wrong
    # wrong_token = {
    #     "user_id": id,
    #     "token": token + "wrong",
    #     "new_password": "rtyrtyrty"
    #     }
    # response4 = client.post(url, wrong_token, format='json')
    # self.assertEqual(response4.status_code, status.HTTP_401_UNAUTHORIZED)

    # #Reset password but user is not exists
    # wrong_user = {
    #     "user_id": "NTM",
    #     "token": token,
    #     "new_password": "rtyrtyrty"
    #     }
    # response5 = client.post(url, wrong_user, format='json')
    # self.assertEqual(response5.status_code, status.HTTP_404_NOT_FOUND)

    # #Reset password but new password is too short
    # short_password = {
    #     "user_id": id,
    #     "token": token,
    #     "new_password": "a"
    #     }
    # response6 = client.post(url, short_password, format='json')
    # self.assertEqual(response6.data["new_password"][0] ,"Пароль должен быть минимум 8 символов")

    # #Reset password but new password is too long
    # long_password = {
    #     "user_id": id,
    #     "token": token,
    #     "new_password": "What's NEKOPARA? Why, it's a cat paradise!"
    #     }
    # response7 = client.post(url, long_password, format='json')
    # self.assertEqual(response7.data["new_password"][0] ,"Пароль должен быть меньше 25 символов")
