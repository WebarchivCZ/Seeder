from django.contrib import admin
from .models import Category, SubCategory, KeyWord


class SlugOrCreateAdminMixin:
    """
    Hides the slug field on add forms and ensures slug_safe runs on save.
    The slug_safe method is defined in the SlugOrCreateModel mixin.
    """
    slug_field = None

    def _slug_field_name(self):
        if self.slug_field:
            return self.slug_field
        model_slug_field = getattr(self.model, "slug_field", None)
        return model_slug_field or "slug"

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None and fields:
            slug_field = self._slug_field_name()
            return tuple(field for field in fields if field != slug_field)
        return fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if hasattr(obj, "slug_safe"):
            obj.slug_safe


@admin.register(Category)
class CategoryAdmin(SlugOrCreateAdminMixin, admin.ModelAdmin):
    """
    Admin interface for Category model
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(SlugOrCreateAdminMixin, admin.ModelAdmin):
    """
    Admin interface for SubCategory model
    """
    list_display = ('name', 'category', 'slug', 'subcategory_id')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category__name', 'name')
    autocomplete_fields = ('category',)


@admin.register(KeyWord)
class KeyWordAdmin(SlugOrCreateAdminMixin, admin.ModelAdmin):
    """
    Admin interface for KeyWord model
    """
    list_display = ('word', 'slug')
    search_fields = ('word',)
    ordering = ('word',)
