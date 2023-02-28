from django.contrib import admin

from .models import Ingredient, MeasurementUnit, Recipe, Tag


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


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    autocomplete_fields = ("ingredient",)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    filter_horizontal = (
        "tags",
        "ingredients",
    )
    inlines = (
        RecipeIngredientInline,
    )
    search_fields = (
        "author__username",
        "name",
        "tags__name",
        "tags__slug",
    )
    readonly_fields = (
        "favorite_count",
    )

    def favorite_count(self, obj):
        return obj.following_users.count()


admin.site.register(Tag, TagAdmin)
admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
