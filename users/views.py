from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.db.models import Q, Exists, Value, BooleanField, Subquery, OuterRef
from .serializers import (
    UserSerializer, RegisterUserSerializer, MyTokenObtainPairSerializer, ChangePasswordSerializer,
    SendPasswordResetEmailSerializer, PasswordResetSerializer, UserMinSerializer, UserNotOwnerSerializer,
    UserSearchSerializer, UpdateUserSerializer
)
from .models import User
from .utils import EMAIL_VERIFICATION_MESSAGE, PASSWORD_RESET_MESSAGE
from django.apps import apps
from .tasks import send_email, delete_inactive

Notification = apps.get_model(app_label="social", model_name="Notification")
Friend = apps.get_model(app_label="social", model_name="Friend")
TeamParticipant = apps.get_model(app_label="title", model_name="TeamParticipant")


class UserDeleteWritePermission(BasePermission):
    message = "Только владелец аккаунта может управлять им"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user


class UserFullInfo(generics.RetrieveAPIView):

    def get_serializer_class(self, *args, **kwargs):
        if self.request and self.request.user.username == self.kwargs.get("username"):
            return UserSerializer
        else:
            return UserNotOwnerSerializer

    def get_object(self):
        username = self.kwargs.get("username")
        if self.request.user.is_anonymous:
            return get_object_or_404(User.objects.annotate(
                requested_friendship=Value(False, output_field=BooleanField()),
                is_friend=Value(False, output_field=BooleanField())
            ), username=username)
        return get_object_or_404(
            User.objects.annotate(
                requested_friendship=Exists(
                    Subquery(Notification.objects.filter(user_id=OuterRef("id"), friend_id=self.request.user.id))
                ),
                is_friend=Exists(
                    Subquery(Friend.objects.filter(user_id=OuterRef("id"), friend_id=self.request.user.id))
                )
            ), username=username)


class UserUpdate(generics.UpdateAPIView, UserDeleteWritePermission):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, UserDeleteWritePermission]
    serializer_class = UpdateUserSerializer

    def patch(self, request, *args, **kwargs):
        user_id = self.kwargs.get("id")
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get("username")
            profile_pic = request.data.get("profile_pic")
            about = serializer.data.get("about")
            birth_date = serializer.data.get("birth_date")
            if user.username != username:
                if User.objects.filter(username__iexact=username).exists():
                    return Response(
                        data={"data": "Это имя пользователя уже занято"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    user.username = username
            if profile_pic is not None:
                user.profile_pic = profile_pic
            if about is not None:
                user.about = about
            if birth_date is not None:
                user.birth_date = birth_date
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDelete(generics.DestroyAPIView, UserDeleteWritePermission):
    permission_classes = [IsAuthenticated, UserDeleteWritePermission]

    def destroy(self, request, *args, **kwargs):
        user_id = self.kwargs.get("id")
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        if not TeamParticipant.objects.filter(user=user).exists():
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                data={"data": "Вы не можете удалить аккаунт, пока находитесь в хотя бы одной команде"},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteProfilePic(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        self.request.user.profile_pic.delete()
        return Response(status=status.HTTP_200_OK)


class UserDetail(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = User.objects.all()
    serializer_class = UserMinSerializer


class UserCreate(APIView):
    def post(self, request):
        reg_serializer = RegisterUserSerializer(data=request.data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            if new_user:
                delete_inactive.apply_async((new_user.id,), countdown=60 * 60 * 24)
                token = default_token_generator.make_token(new_user)
                send_email.delay(
                    EMAIL_VERIFICATION_MESSAGE["subject"],
                    EMAIL_VERIFICATION_MESSAGE["message"].format(
                        urlsafe_base64_encode(force_bytes(new_user.id)),
                        token
                    ),
                    [new_user.email],
                )
                return Response(status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class EmailOrUsernameLogin(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        user = user_model._default_manager.filter(
            Q(username__iexact=username) | Q(email__iexact=User.objects.normalize_email(username))
        ).first()
        if user and user.check_password(password):
            if not user.is_active:
                token = default_token_generator.make_token(user)
                send_email.delay(
                    EMAIL_VERIFICATION_MESSAGE["subject"],
                    EMAIL_VERIFICATION_MESSAGE["message"].format(urlsafe_base64_encode(force_bytes(user.id)), token),
                    [user.email]
                )
            return user
        else:
            user_model().set_password(password)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": "Неверный пароль"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Пароль успешно изменен"
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistrationView(APIView):
    def post(self, request):
        user_id = urlsafe_base64_decode(request.data["user_id"])
        token = request.data["token"]
        try:
            user = User.objects.get(id=user_id)
            if user.is_active:
                return Response({"data": "Аккаунт уже активирован"}, status=status.HTTP_401_UNAUTHORIZED)
            elif default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"data": "Аккаунт успешно активирован"}, status=status.HTTP_200_OK)
            else:
                return Response({"data": "Время на использование ключа активации истекло или он недействителен"},
                                status=status.HTTP_401_UNAUTHORIZED
                                )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user_id = urlsafe_base64_decode(serializer.data.get("user_id"))
            new_password = serializer.data.get("new_password")
            token = serializer.data.get("token")
            try:
                user = User.objects.get(id=user_id)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({"data": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
                else:
                    return Response({"data": "Время на использование ключа активации истекло или он недействителен"},
                                    status=status.HTTP_401_UNAUTHORIZED
                                    )
            except User.DoesNotExist:
                return Response({"data": "Пользователь не существует"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetEmailView(APIView):
    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            user = User.objects.get(email__exact=email)
            token = default_token_generator.make_token(user)
            send_email.delay(
                PASSWORD_RESET_MESSAGE["subject"],
                PASSWORD_RESET_MESSAGE["message"].format(urlsafe_base64_encode(force_bytes(user.id)), token),
                [user.email]
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer

    def get_queryset(self):
        return User.objects.filter(username__icontains=self.kwargs.get("username"))
