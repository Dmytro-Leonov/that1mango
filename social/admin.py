from django.contrib import admin
from .models import Friend, Comment, CommentVote, Notification, ListTitle, List, Subscription


class FriendAdmin(admin.ModelAdmin):
    model = Friend
    list_display = ("id", "user", "friend")
    fieldsets = (
        (None, {
            "fields": ("user", "friend")
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("user", "friend")
        return self.readonly_fields


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    ordering = ("-creation_date",)
    list_display = ("id", "title", "user", "comment", "likes", "dislikes", "creation_date", "is_deleted")
    fieldsets = (
        (None, {
            "fields": ("title", "user", "comment", "reply_to", "likes", "dislikes", "is_deleted")
        }),
    )
    readonly_fields = ("likes", "dislikes")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("title", "user", "comment", "reply_to", "likes", "dislikes")
        return self.readonly_fields


class CommentVoteAdmin(admin.ModelAdmin):
    model = CommentVote
    list_display = ("id", "user", "comment", "vote")
    fieldsets = (
        (None, {
            "fields": ("user", "comment", "vote")
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("user", "comment", "vote")
        return self.readonly_fields


class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    list_display = ("id", "user", "friend", "team", "title", "chapter", "type", "created_at", "is_read")
    fieldsets = (
        (None, {
            "fields": ("user", "friend", "team", "title", "chapter", "type", "created_at", "is_read")
        }),
    )
    readonly_fields = ("created_at",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                "user", "friend", "team", "title", "chapter", "type", "created_at", "is_read"
            )
        return self.readonly_fields


class ListTitleAdmin(admin.ModelAdmin):
    model = ListTitle
    list_display = ("id", "list", "title", "date_added")
    ordering = ("-date_added",)
    fieldsets = (
        (None, {
            "fields": ("list", "title", "date_added")
        }),
    )
    readonly_fields = ("date_added",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("list", "title", "date_added")
        return self.readonly_fields


class ListAdmin(admin.ModelAdmin):
    model = List
    list_display = ("id", "user", "name", "hidden", "titles_count")
    fieldsets = (
        (None, {
            "fields": ("user", "name", "hidden", "titles_count")
        }),
    )
    readonly_fields = ("titles_count",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("user", "user", "name", "hidden")
        return self.readonly_fields


class SubscriptionAdmin(admin.ModelAdmin):
    model = Subscription
    list_display = ("user", "title", "team")
    fieldsets = (
        (None, {
            "fields": ("user", "title", "team")
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("user", "title", "team")
        return self.readonly_fields


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(ListTitle, ListTitleAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentVote, CommentVoteAdmin)
admin.site.register(Friend, FriendAdmin)
