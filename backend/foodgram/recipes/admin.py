from django.contrib import admin

from .models import Ingredient, MeasurementUnit, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )


class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
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


admin.site.register(Tag, TagAdmin)
admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
