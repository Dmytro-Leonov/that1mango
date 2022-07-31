from django.contrib import admin
from .models import (
    Title, ReleaseFormat, Rating, TitleRating, TitlePerson, Person, Keyword, Publisher, Chapter, Team, TeamParticipant,
    UserTitleRating, ChapterLikes, TitlePublisher, TitleTeam, ChapterImages
)
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin


class PersonInlineAdmin(admin.TabularInline):
    model = TitlePerson
    extra = 1


class PublisherInlineAdmin(admin.TabularInline):
    model = TitlePublisher
    extra = 1


class TitleAdmin(admin.ModelAdmin, DynamicArrayMixin):
    model = Title
    ordering = ("-date_added",)
    list_display = ("name", "english_name", "title_status", "date_added")
    prepopulated_fields = {"slug": ("english_name",)}
    fieldsets = (
        ("Names", {"fields": ("name", "english_name", "slug", "alternative_names")}),
        ("Info", {"fields": (
            "description", "release_year", "poster", "chapters", "licensed", "age_rating", "title_type", "title_status"
        )}),
        ("Related", {"fields": ("chapter_count", "in_lists", "release_format", "keywords")}),
    )
    inlines = (PersonInlineAdmin, PublisherInlineAdmin)
    filter_horizontal = ("release_format", "keywords", "publisher")
    readonly_fields = ("chapter_count", "in_lists")


class ReleaseFormatAdmin(admin.ModelAdmin):
    model = ReleaseFormat
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug")}),
    )


class TitleRatingAdmin(admin.ModelAdmin):
    model = TitleRating
    list_display = ("title", "rating", "amount")
    fieldsets = (
        (None, {"fields": ("title", "rating", "amount")}),
    )
    # readonly_fields = ("amount",)


class RatingAdmin(admin.ModelAdmin):
    model = Rating
    list_display = ("id", "mark")
    # list_display = ("id", "mark", "description")
    fieldsets = (
        (None, {"fields": ("mark",)}),
        # (None, {"fields": ("mark", "description")}),
    )


class KeywordAdmin(admin.ModelAdmin):
    model = Keyword
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "type")}),
    )


class PersonAdmin(admin.ModelAdmin, DynamicArrayMixin):
    model = Person
    list_display = ("name", "alternative_names", "description")
    fieldsets = (
        (None, {"fields": ("name", "alternative_names", "picture", "description")}),
    )


class PublisherAdmin(admin.ModelAdmin, DynamicArrayMixin):
    model = Publisher
    list_display = ("name", "slug", "alternative_names", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "alternative_names", "picture", "description")}),
    )


class ChapterAdmin(admin.ModelAdmin):
    model = Chapter
    list_display = ("title", "team", "name", "volume_number", "chapter_number", "is_published", "image_archive", "likes")
    fieldsets = (
        (None, {"fields": ("title", "team", "name", "volume_number", "chapter_number", "is_published", "image_archive", "likes")}),
    )
    readonly_fields = ("likes", "image_archive")
    # readonly_fields = ("team", "title")


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "picture", "description")}),
    )


class TeamParticipantAdmin(admin.ModelAdmin, DynamicArrayMixin):
    model = TeamParticipant
    list_display = ("id", "team", "user", "roles")
    fieldsets = (
        (None, {"fields": ("team", "user", "roles")}),
    )


class UserTitleRatingAdmin(admin.ModelAdmin):
    model = UserTitleRating
    list_display = ("user", "title", "rating")
    fieldsets = (
        (None, {"fields": ("user", "title", "rating")}),
    )


class ChapterLikesAdmin(admin.ModelAdmin):
    model = UserTitleRating
    list_display = ("user", "chapter", "date_added")
    fieldsets = (
        (None, {"fields": ("user", "chapter", "date_added")}),
    )
    readonly_fields = ("date_added",)


class TitleTeamAdmin(admin.ModelAdmin):
    model = TitlePerson
    list_display = ("title", "team")
    fieldsets = (
        (None, {"fields": ("title", "team")}),
    )


class ChapterImagesAdmin(admin.ModelAdmin):
    model = ChapterImages
    list_display = ("id", "chapter", "image")
    fieldsets = (
        (None, {"fields": ("chapter", "image")}),
    )


admin.site.register(ChapterImages, ChapterImagesAdmin)
admin.site.register(TitleTeam, TitleTeamAdmin)
admin.site.register(ChapterLikes, ChapterLikesAdmin)
admin.site.register(UserTitleRating, UserTitleRatingAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamParticipant, TeamParticipantAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(TitleRating, TitleRatingAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(ReleaseFormat, ReleaseFormatAdmin)
