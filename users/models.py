from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from PIL import Image

PROFILE_PIC_SIZE = (350, 350)


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, birth_date, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must be assigned to is_superuser=True.")
        return self.create_user(email, username, birth_date, password, **other_fields)

    def create_user(self, email, username, birth_date, password, **other_fields):
        if not email:
            raise ValueError(_("You must provide an email address"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, birth_date=birth_date, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(_("username"), validators=[MinLengthValidator(3)], max_length=30, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    birth_date = models.DateField(blank=False, null=False)
    profile_pic = models.ImageField(_("profile picture"), upload_to="profile_pictures/%Y/%m", blank=True)
    about = models.TextField(_("about"), max_length=200, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="social.Friend",
        verbose_name=_("friends with"),
        related_name="friends_of_user"
    )
    comments = models.ManyToManyField(
        "social.Comment",
        through="social.CommentVote",
        verbose_name=_("comments"),
        related_name="users_of_comment"
    )
    subscriptions = models.ManyToManyField(
        "title.Title",
        verbose_name=_("subscriptions"),
        related_name="subscribed_users"
    )

    objects = CustomAccountManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "birth_date"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_pic:
            profile_pic = Image.open(self.profile_pic.path)
            img_width, img_height = profile_pic.size
            crop_size = min([img_width, img_height])
            profile_pic = profile_pic.crop(
                (
                    (img_width - crop_size) // 2,
                    (img_height - crop_size) // 2,
                    (img_width + crop_size) // 2,
                    (img_height + crop_size) // 2
                )
            )
            profile_pic.thumbnail(PROFILE_PIC_SIZE)
            profile_pic.save(self.profile_pic.path)

    def __str__(self):
        return self.username
