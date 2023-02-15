from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    ordering = ("pk",)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return ("pk", ) + list_display  # type:ignore


admin.site.register(User, CustomUserAdmin)
