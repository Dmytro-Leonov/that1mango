from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField
from PIL import Image
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from model_utils import FieldTracker
from cloudinary.models import CloudinaryField as BaseCloudinaryField
import cloudinary
import pgtrigger
import datetime


PICTURE_SIZE = (350, 350)


class ReleaseFormat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Release format name"), max_length=10, unique=True, blank=False, null=False)
    slug = models.SlugField(db_index=True, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name


class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    mark = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10)], unique=True, blank=False, null=False)

    class Meta:
        ordering = ("-mark",)

    def __str__(self):
        return f"Оценка {self.mark}"


class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("publisher name"), max_length=30, unique=True, blank=False, null=False)
    slug = models.SlugField(db_index=True, unique=True, blank=False, null=False)
    alternative_names = ArrayField(
        models.CharField(max_length=200, unique=True),
        size=5,
        blank=False,
        null=False,
        verbose_name=_("alternative names")
    )
    picture = models.ImageField(_("Publisher picture"), upload_to="publishers/pictures/%Y", blank=True)
    description = models.TextField(_("description"), max_length=1000, blank=True, null=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            picture = Image.open(self.picture.path)
            picture.thumbnail(PICTURE_SIZE)
            picture.save(self.picture.path)

    def __str__(self):
        return str(self.name)


class Person(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("person name"), max_length=30, unique=True, blank=False, null=False)
    alternative_names = ArrayField(
        models.CharField(max_length=200, unique=True),
        size=5,
        blank=False,
        null=False,
        verbose_name=_("alternative names")
    )
    picture = models.ImageField(_("Person picture"), upload_to="persons/pictures/%Y", blank=True)
    description = models.TextField(_("description"), max_length=1000, blank=True, null=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            picture = Image.open(self.picture.path)
            picture.thumbnail(PICTURE_SIZE)
            picture.save(self.picture.path)

    def __str__(self):
        return str(self.name)


class Keyword(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("keyword name"), max_length=30, unique=True, blank=False, null=False)
    slug = models.SlugField(db_index=True, unique=True, blank=False, null=False)

    class KeyWordType(models.TextChoices):
        GENRE = "Genre", _("Жанр")
        TAG = "Tag", _("Тег")

    type = models.CharField(
        max_length=5,
        choices=KeyWordType.choices,
        default=KeyWordType.GENRE,
        blank=False,
        null=False
    )

    def __str__(self):
        return str(self.name)


class Title(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("title name"), max_length=200, unique=True, blank=False, null=False)
    slug = models.SlugField(db_index=True, unique=True, null=False)
    english_name = models.CharField(_("english name"), max_length=200, unique=True, blank=False, null=False)
    alternative_names = ArrayField(
        models.CharField(max_length=200, unique=True),
        size=10,
        blank=False,
        null=False,
        verbose_name=_("alternative names")
    )
    description = models.TextField(_("description"), max_length=1500, blank=False, null=False)
    release_year = models.IntegerField(
        _("release year"),
        validators=[
            MinValueValidator(1900, _("Release year must be greater than 1900")),
            MaxValueValidator(
                datetime.date.today().year,
                _(f"Release year must be less than or equal to {datetime.date.today().year}")
            )
        ],
        default=datetime.date.today().year,
        blank=False,
        null=False
    )
    poster = models.ImageField(_("title poster"), upload_to="titles/posters/%Y/%m", blank=False)
    chapters = models.PositiveSmallIntegerField(blank=True, null=True)
    chapter_count = models.PositiveIntegerField(_("chapter count"), default=0, blank=True, null=False)
    in_lists = models.PositiveIntegerField(_("in lists"), default=0, blank=True, null=False)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=False)
    licensed = models.BooleanField(verbose_name=_("licensed"), blank=False, null=False)

    class TitleAgeRating(models.TextChoices):
        EVERYONE = "E", _("Все возраста")
        YOUTH = "Y", _("10+")
        TEENS = "T", _("13+")
        OLDER_TEENS = "OT", _("16+")
        MATURE = "M", _("18+")

    age_rating = models.CharField(
        max_length=2,
        choices=TitleAgeRating.choices,
        default=TitleAgeRating.EVERYONE,
        blank=False,
        null=False
    )

    class TitleType(models.TextChoices):
        MANGA = "Manga", _("Манга")
        MANHWA = "Manhwa", _("Манхва")
        MANHUA = "Manhua", _("Маньхуа")

    title_type = models.CharField(
        max_length=10,
        choices=TitleType.choices,
        default=TitleType.MANGA,
        blank=False,
        null=False
    )

    class TitleStatus(models.TextChoices):
        ANNOUNCEMENT = "Announcement", _("Анонс")
        ONGOING = "Ongoing", _("Онгоинг")
        FINISHED = "Finished", _("Завершен")
        SUSPENDED = "Suspended", _("Приостановлен")
        STOPPED = "Stopped", _("Выпуск прекращен")

    title_status = models.CharField(
        max_length=12,
        choices=TitleStatus.choices,
        default=TitleStatus.ANNOUNCEMENT,
        blank=False,
        null=False
    )

    release_format = models.ManyToManyField(
        ReleaseFormat,
        verbose_name=_("release formats"),
        related_name="titles_with_release_format"
    )
    title_rating = models.ManyToManyField(
        Rating,
        verbose_name=_("title rating"),
        through="TitleRating",
        related_name="titles_with_rating"
    )
    publisher = models.ManyToManyField(
        Publisher,
        verbose_name=_("title publisher"),
        through="TitlePublisher",
        related_name="titles_of_publisher"
    )
    person = models.ManyToManyField(
        Person,
        verbose_name=_("title person"),
        through="TitlePerson",
        related_name="titles_of_person"
    )
    keywords = models.ManyToManyField(
        Keyword,
        verbose_name=_("title keyword"),
        related_name="titles_of_keyword"
    )
    teams = models.ManyToManyField(
        "Team",
        verbose_name=_("title teams"),
        through="TitleTeam",
    )
    tracker = FieldTracker(fields=["title_status"])

    def __str__(self):
        return self.name


@receiver(post_save, sender=Title)
def title_status_update(sender, instance, **kwargs):
    if instance.id:
        if instance.title_status != instance.tracker.previous("title_status"):
            from .tasks import notify_users_of_new_title_status
            notify_users_of_new_title_status.delay(instance.id)


class TitleTeam(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.ForeignKey(Title, related_name="teams_of_title", on_delete=models.CASCADE, blank=False, null=False)
    team = models.ForeignKey("Team", related_name="titles_of_team", on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ["title", "team"]


class TitleRating(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.ForeignKey(Title, related_name="ratings_of_title", on_delete=models.CASCADE, blank=False, null=False)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, blank=False, null=False)
    amount = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        unique_together = ["title", "rating"]


class TitlePerson(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.ForeignKey(Title, related_name="persons_of_title", on_delete=models.CASCADE, blank=False, null=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False,
                               null=False
                               )

    class TitleRole(models.TextChoices):
        AUTHOR = "Author", _("Автор")
        ARTIST = "Artist", _("Художник")

    title_role = models.CharField(
        max_length=12,
        choices=TitleRole.choices,
        blank=False,
        null=False
    )

    class Meta:
        unique_together = ["title", "person", "title_role"]


class TitlePublisher(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.ForeignKey(Title, related_name="publishers_of_title", on_delete=models.CASCADE, blank=False,
                              null=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ["title", "publisher"]


@pgtrigger.register(
    pgtrigger.Trigger(
        name="delete_if_exists_on_user_vote",
        operation=pgtrigger.Insert,
        when=pgtrigger.Before,
        func=
        """
        delete from title_usertitlerating
        WHERE title_id = new.title_id AND user_id = new.user_id;
        RETURN NEW;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_title_rating_on_user_vote_update",
        operation=pgtrigger.Update,
        when=pgtrigger.After,
        func=
        """
        UPDATE title_titlerating
        SET amount = amount - 1
        WHERE title_id = OLD.title_id AND rating_id = OLD.rating_id;
        UPDATE title_titlerating
        SET amount = amount + 1
        WHERE title_id = NEW.title_id AND rating_id = NEW.rating_id;
        RETURN NEW;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_title_rating_on_user_vote_delete",
        operation=pgtrigger.Delete,
        when=pgtrigger.After,
        func=
        """
        UPDATE title_titlerating
        SET amount = amount - 1
        WHERE title_id = OLD.title_id AND rating_id = OLD.rating_id;
        RETURN OLD;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_title_rating_on_user_vote",
        operation=pgtrigger.Insert,
        when=pgtrigger.After,
        func=
        """
        if EXISTS (SELECT 1 FROM title_titlerating WHERE title_id = NEW.title_id AND rating_id = NEW.rating_id ) then 
            UPDATE title_titlerating
            SET amount = amount + 1
            WHERE title_id = NEW.title_id AND rating_id = NEW.rating_id;
        ELSE
            INSERT INTO title_titlerating (title_id, rating_id, amount)
            values (NEW.title_id, NEW.rating_id, 1);
        END IF;
        RETURN NEW;
        """
    )
)
class UserTitleRating(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="title_ratings_for_user", on_delete=models.CASCADE,
                             blank=False, null=False)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, blank=False, null=False)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ["user", "title"]

    def __str__(self):
        return f"{self.user} - {self.title}: {self.rating}"


class TeamParticipant(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False
    )
    team = models.ForeignKey(
        "Team", related_name="team_participants", on_delete=models.CASCADE, blank=False, null=False
    )

    class Role(models.TextChoices):
        ADMIN = "admin", _("Админ")
        TRANSLATOR = "translator", _("Переводчик")
        CLEANER = "cleaner", _("Клинер")
        TYPESETTER = "typesetter", _("Тайпер")
        EDITOR = "editor", _("Эдитор")
        CORRECTOR = "corrector", _("Корректор")
        BETA_READER = "beta_reader", _("Бета читатель")
        SCANNER = "scanner", _("Сканер")
        UPLOADER = "uploader", _("Загрузчик")

    roles = ArrayField(
        models.CharField(
            max_length=11,
            choices=Role.choices,
            blank=False,
            null=False
        ),
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ["user", "team"]


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("team name"), max_length=30, unique=True, blank=False, null=False)
    slug = models.SlugField(db_index=True, unique=True, blank=False, null=False)
    picture = models.ImageField(_("Team picture"), upload_to="teams/pictures/%Y", blank=True)
    description = models.TextField(_("description"), max_length=300, blank=True, null=False)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through=TeamParticipant,
        verbose_name=_("team participants"),
        related_name="teams_of_user"
    )
    titles = models.ManyToManyField(
        Title,
        through="Chapter",
        verbose_name=_("team titles"),
        related_name="teams_of_title_through_chapter"
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            picture = Image.open(self.picture.path)
            picture.thumbnail(PICTURE_SIZE)
            picture.save(self.picture.path)

    def __str__(self):
        return self.name


@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_chapter_count_and_title_teams_on_insert",
        operation=pgtrigger.Insert,
        when=pgtrigger.After,
        func=
        """
        if not exists(select id from title_titleteam where title_id = new.title_id and team_id = new.team_id) then
            insert into title_titleteam (title_id, team_id)
            values (new.title_id, new.team_id);
        end if;
        if (select count(*) from title_chapter where team_id = new.team_id and title_id = new.title_id) =
        (select chapter_count from title_title where id = new.title_id) + 1 then
            update title_title
            set chapter_count = chapter_count + 1
            where id = new.title_id;
        end if;
        return null;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_chapter_count_on_chapter_delete",
        operation=pgtrigger.Delete,
        when=pgtrigger.After,
        func=
        """
        update title_title
        set chapter_count = (
            select coalesce(max(team_chapters), 0)
        from (
            select count(*) as team_chapters
            from title_chapter
            where title_id = old.title_id
            group by team_id
        ) as subquery)
        where id = old.title_id;
        if not exists(select id from title_chapter where title_id = old.title_id and team_id = old.team_id) then
            delete from title_titleteam
            where title_id = old.title_id and team_id = old.team_id;
        end if;
        return old;
        """
    )
)
class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.ForeignKey(
        Title, related_name="chapters_of_title", on_delete=models.CASCADE, blank=False, null=False
    )
    team = models.ForeignKey(Team, related_name="chapters_of_team", on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(_("chapter name"), max_length=100, blank=True, null=False)
    volume_number = models.PositiveSmallIntegerField(blank=False, null=False)
    chapter_number = models.FloatField(validators=[MinValueValidator(0)], blank=False, null=False)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=False)
    likes = models.IntegerField(default=0, blank=True, null=False)
    is_published = models.BooleanField(default=False, blank=True, null=False)
    image_archive = models.FileField(
        _("archive with chapter pages"), upload_to="titles/chapters", null=True, blank=False
    )
    user_likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ChapterLikes",
        verbose_name=_("User likes"),
        related_name="liked_chapters"
    )

    class Meta:
        unique_together = ["volume_number", "chapter_number", "title", "team"]

    def __str__(self):
        return f"{self.title.name} - Том {self.volume_number} Глава {self.chapter_number}"


class CloudinaryImage(BaseCloudinaryField):
    def upload_options(self, instance):
        return {
            "folder": f"{instance.chapter.title.slug}/c{instance.chapter.id}",
            "unique_filename": True,
            "resource_type": "image",
            "quality": "auto:eco"
        }

    def pre_save(self, model_instance, add):
        self.options = self.options | self.upload_options(model_instance)
        super().pre_save(model_instance, add)
        return model_instance.image


class ChapterImages(models.Model):
    id = models.AutoField(primary_key=True)
    chapter = models.ForeignKey(
        Chapter, related_name="images_of_chapter", on_delete=models.CASCADE, blank=False, null=True
    )
    image = CloudinaryImage()


@receiver(pre_delete, sender=ChapterImages)
def image_delete_on_delete(sender, instance, **kwargs):
    if instance.image:
        cloudinary.uploader.destroy(instance.image.public_id)


@receiver(pre_save, sender=ChapterImages)
def image_delete_on_update(sender, instance, **kwargs):
    if instance.id:
        ci = ChapterImages.objects.get(id=instance.id)
        if ci.image:
            cloudinary.uploader.destroy(ci.image.public_id)


@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_chapter_likes_on_user_like_delete",
        operation=pgtrigger.Delete,
        when=pgtrigger.After,
        func=
        """
        UPDATE title_chapter
        SET likes = likes - 1
        WHERE id = OLD.chapter_id;
        RETURN NULL;
        """
    )
)
@pgtrigger.register(
    pgtrigger.Trigger(
        name="update_chapter_likes_on_user_like",
        operation=pgtrigger.Insert,
        when=pgtrigger.After,
        func=
        """
        UPDATE title_chapter
        SET likes = likes + 1
        WHERE id = NEW.chapter_id;
        RETURN NEW;
        """
    )
)
class ChapterLikes(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=True)
    chapter = models.ForeignKey(
        Chapter, related_name="likes_for_chapter", on_delete=models.CASCADE, blank=False, null=True
    )
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=False)

    class Meta:
        unique_together = ["user", "chapter"]

    def __str__(self):
        return f"{self.user.username} liked {self.chapter.name}"
