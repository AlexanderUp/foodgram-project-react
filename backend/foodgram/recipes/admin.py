from django.contrib import admin

from .models import Tag  # isort:skip


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )


admin.site.register(Tag, TagAdmin)
