from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.utils.http import urlsafe_base64_decode
import datetime
from dateutil.relativedelta import relativedelta
from .models import User

PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH = 8, 25
OLDEST_POSSIBLE, YOUNGEST_POSSIBLE = 100, 3


class TeamSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    picture = serializers.ImageField()

    class Meta:
        fields = ("id", "name", "slug", "picture")


class UserMinSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "profile_pic", "is_staff", "birth_date")


class UserSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(source="teams_of_user", many=True, required=False)
    profile_pic = serializers.ImageField()
    email = serializers.EmailField(required=False)
    friends = UserMinSerializer(source="friends_of_user", many=True)
    requested_friendship = serializers.BooleanField()
    is_friend = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "profile_pic", "birth_date", "about", "start_date", "is_staff", "is_active",
            "teams", "friends", "requested_friendship", "is_friend"
        )


class UpdateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(regex="^(([A-Za-z-_0-9]{0,30}))$", message="Некорректный логин"),
            MinLengthValidator(3, message="Логин должен состоять минимум из 3 символов"),
            MaxLengthValidator(30, message="Логин не должен превышать 30 символов")
        ]
    )
    birth_date = serializers.DateField()
    profile_pic = serializers.ImageField(required=False)

    def validate_birth_date(self, birth_date):
        if birth_date < datetime.date.today() - relativedelta(years=OLDEST_POSSIBLE):
            raise serializers.ValidationError("Некорректная дата рождения")
        if birth_date > datetime.date.today() - relativedelta(years=YOUNGEST_POSSIBLE):
            raise serializers.ValidationError("Некорректная дата рождения")
        return birth_date

    class Meta:
        model = User
        fields = ("username", "profile_pic", "about", "birth_date")


class UserNotOwnerSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(source="teams_of_user", many=True)
    friends = UserMinSerializer(source="friends_of_user", many=True)
    requested_friendship = serializers.BooleanField()
    is_friend = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "id", "username", "profile_pic", "about", "start_date", "is_staff", "is_active", "teams", "friends",
            "requested_friendship", "is_friend"
            )


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Имя пользователя не попало на сервер"
        },
        validators=[
            RegexValidator(regex="^(([A-Za-z-_0-9]{0,30}))$", message="Некорректный логин"),
            MinLengthValidator(3, message="Логин должен состоять минимум из 3 символов"),
            MaxLengthValidator(30, message="Логин не должен превышать 30 символов")
        ]
    )
    email = serializers.EmailField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Email не попал на сервер",
            "invalid": "Некорректный email"
        }
    )
    password = serializers.CharField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Пароль не попал на сервер"
        }
    )
    birth_date = serializers.DateField()

    def validate_username(self, username):
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("Это имя пользователя уже занято")
        return username

    def validate_email(self, email):
        if User.objects.filter(email__iexact=User.objects.normalize_email(email)).exists():
            raise serializers.ValidationError("Этот email уже зарегестрирован")
        return email

    def validate_password(self, password):
        if len(password) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(f"Пароль должен быть минимум {PASSWORD_MIN_LENGTH} символов")
        elif len(password) > PASSWORD_MAX_LENGTH:
            raise serializers.ValidationError(f"Пароль должен быть меньше {PASSWORD_MAX_LENGTH} символов")
        return password

    def validate_birth_date(self, birth_date):
        if birth_date < datetime.date.today() - relativedelta(years=OLDEST_POSSIBLE):
            raise serializers.ValidationError("Некорректная дата рождения")
        if birth_date > datetime.date.today() - relativedelta(years=YOUNGEST_POSSIBLE):
            raise serializers.ValidationError("Некорректная дата рождения")
        return birth_date

    class Meta:
        model = User
        fields = ("email", "username", "birth_date", "password")
        extra_kwargs = {
            "password": {
                "write_only": True
            },
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["is_superuser"] = user.is_superuser
        return token


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Пароль не попал на сервер"
        })

    def validate_new_password(self, password):
        if len(password) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(f"Пароль должен быть минимум {PASSWORD_MIN_LENGTH} символов")
        elif len(password) > PASSWORD_MAX_LENGTH:
            raise serializers.ValidationError(f"Пароль должен быть меньше {PASSWORD_MAX_LENGTH} символов")
        return password

    class Meta:
        model = User


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Email не попал на сервер",
            "invalid": "Некорректный email"
        }
    )

    def validate_email(self, email):
        if not User.objects.filter(email__exact=User.objects.normalize_email(email)).exists():
            raise serializers.ValidationError("Аккаунт не найден")
        return email
    
    class Meta:
        model = User


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        error_messages={
            "blank": "Поле не должно быть пустым",
            "required": "Пароль не попал на сервер"
        })
    user_id = serializers.CharField(
        error_messages={
            "blank": "ID пользователя не должно быть пустым",
            "required": "ID пользователя не попал на сервер",
            "invalid": "Некорректный ID пользователя"
        }
    )
    token = serializers.CharField()

    def validate_user_id(self, user_id):
        try:
            int(urlsafe_base64_decode(user_id))
        except ValueError:
            raise serializers.ValidationError("Некорректный ID пользователя")
        return user_id

    def validate_new_password(self, password):
        if len(password) < PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(f"Пароль должен быть минимум {PASSWORD_MIN_LENGTH} символов")
        elif len(password) > PASSWORD_MAX_LENGTH:
            raise serializers.ValidationError(f"Пароль должен быть меньше {PASSWORD_MAX_LENGTH} символов")
        return password

    class Meta:
        model = User


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "profile_pic")
