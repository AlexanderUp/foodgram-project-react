from django.contrib import admin

from .models import Ingredient, MeasurementUnit, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )


class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
    )
    search_fields = (
        "name",
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit",
    )
    list_select_related = (
        "measurement_unit",
    )
    search_fields = (
        "name",
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
