from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ("email", "username",)
    list_filter = ("is_active", "is_staff")
    ordering = ("-start_date",)
    list_display = ("id", "username", "email", "is_active", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "username")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
        ("Personal", {"fields": ("profile_pic", "birth_date", "about")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "username", "birth_date", "profile_pic", "password1", "password2", "is_active", "is_staff"
            )}
         ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("email", "birth_date")
        return self.readonly_fields


admin.site.register(User, UserAdminConfig)
