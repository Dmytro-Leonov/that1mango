from django.db import models
from django.db.models import UniqueConstraint, Q
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import pgtrigger


class Friend(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name="friends_user",
        blank=False, null=False
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friends_friend",
        verbose_name=_("friend"),
        blank=False, null=False
    )

    class Meta:
        unique_together = ["user", "friend"]

    def __str__(self):
        return f"{self.user} -> {self.friend}"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.ForeignKey("title.Title", on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("user"),
        related_name="comments_of_user",
        blank=False, null=True
    )
    reply_to = models.ForeignKey(
        "social.Comment",
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("reply to"),
        blank=True, null=True
    )
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=False)
    comment = models.TextField(_("comment"), max_length=1500, blank=False, null=False)
    is_deleted = models.BooleanField(default=False, blank=True, null=False)
    likes = models.PositiveIntegerField(default=0, blank=True, null=False)
    dislikes = models.PositiveIntegerField(default=0, blank=True, null=False)

    def __str__(self):
        return f"{self.id}: {self.comment[:20]}"


@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_comment_likes_on_insert",
        operation=pgtrigger.Insert,
        when=pgtrigger.Before,
        func=
        """
        delete from social_commentvote
        where comment_id = new.comment_id and user_id = new.user_id and vote != new.vote;
        if new.vote = true then
            update social_comment
            set likes = likes + 1
            where id = new.comment_id;
        else
            update social_comment
            set dislikes = dislikes + 1
            where id = new.comment_id;
        end if;
        return new;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_comment_likes_on_delete",
        operation=pgtrigger.Delete,
        when=pgtrigger.Before,
        func=
        """
        if old.vote = true then
            update social_comment
            set likes = likes - 1
            where id = old.comment_id;
        else
            update social_comment
            set dislikes = dislikes - 1
            where id = old.comment_id;
        end if;
        return null;
        """
    )
)
class CommentVote(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_votes_of_user",
        blank=False, null=False
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="comment_votes_of_comment",
        blank=False, null=False
    )
    vote = models.BooleanField(blank=False, null=False)

    class Meta:
        unique_together = ["user", "comment", "vote"]


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=False, null=False
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    title = models.ForeignKey(
        "title.Title",
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    chapter = models.ForeignKey(
        "title.Chapter",
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    team = models.ForeignKey(
        "title.Team",
        on_delete=models.CASCADE,
        blank=True, null=True
    )

    class NotificationType(models.IntegerChoices):
        NEW_CHAPTER = 1, _("Вышла новая глава")
        STATUS_CHANGED = 2, _("У тайтла изменился статус")
        FRIEND_REQUEST = 3, _("Новый запрос в друзья")
        FRIEND_ACCEPTED = 4, _("Пользователь подтвердил ваш запрос на дружбу")
        JOIN_TEAM_REQUEST = 5, _("Вас пригласили вступить в команду переводчиков")
        TEAM_KICK = 6, _("Вас исключили из команды переводчиков")
        COMMENT_REPLY = 7, _("Пользователь дал ответ на ваш комментарий")
        CHAPTER_UPLOAD_SUCCESS = 8, _("Глава была успешно загружена")
        CHAPTER_UPLOAD_FAIL = 9, _("Возникла ошибка при загрузке главы")
        CHAPTER_UPDATE_SUCCESS = 10, _("Глава была успешно обновлена")
        CHAPTER_UPDATE_FAIL = 11, _("Возникла ошибка при обновлении главы")

    type = models.PositiveSmallIntegerField(
        choices=NotificationType.choices,
        blank=False,
        null=False
    )
    is_read = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_in_list_count_on_update",
        operation=pgtrigger.Update,
        when=pgtrigger.After,
        func=
        """
        update social_list
        set titles_count = titles_count - 1
        where id = old.list_id;
        update social_list
        set titles_count = titles_count + 1
        where id = new.list_id;
        return null;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_in_list_count_on_delete",
        operation=pgtrigger.Delete,
        when=pgtrigger.After,
        func=
        """
        update social_list
        set titles_count = titles_count - 1
        where id = old.list_id;
        update title_title
        set in_lists = in_lists - 1
        where id = old.title_id;
        return old;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_in_list_count_on_insert",
        operation=pgtrigger.Insert,
        when=pgtrigger.After,
        func=
        """
        update social_list
        set titles_count = titles_count + 1
        where id = new.list_id;
        update title_title
        set in_lists = in_lists + 1
        where id = new.title_id;
        return null;
        """
    )
)
class ListTitle(models.Model):
    id = models.AutoField(primary_key=True)
    list = models.ForeignKey(
        "social.List",
        on_delete=models.CASCADE,
        blank=False, null=False
    )
    title = models.ForeignKey(
        "title.Title",
        related_name="lists_of_title",
        on_delete=models.CASCADE,
        blank=False, null=False
    )
    date_added = models.DateTimeField(auto_now=True, blank=True, null=False)

    class Meta:
        unique_together = ["list", "title"]


class List(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name="user_lists",
        blank=False, null=False
    )
    name = models.CharField(_("list name"), max_length=30, blank=False, null=False)
    hidden = models.BooleanField(_("hidden"), default=False, blank=False, null=False)
    titles_count = models.PositiveIntegerField("titles in list", default=0, blank=True, null=False)
    titles = models.ManyToManyField(
        "title.Title",
        through=ListTitle,
        verbose_name=_("titles"),
        related_name="title_lists"
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["user", "name"]
        ordering = ("id",)


class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="user_subscriptions",
        on_delete=models.CASCADE,
        blank=False, null=False
    )
    title = models.ForeignKey(
        "title.Title",
        related_name="title_subscriptions",
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    team = models.ForeignKey(
        "title.Team",
        on_delete=models.CASCADE,
        blank=True, null=True
    )

    class Meta:
        unique_together = ["user", "title", "team"]
        constraints = [
            UniqueConstraint(
                name="social_subscription_user_title_unique",
                fields=("user", "title"),
                condition=Q(team__isnull=True)
            )
        ]
