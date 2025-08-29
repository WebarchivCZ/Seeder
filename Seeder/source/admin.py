from django.contrib import admin
from .models import Category, SubCategory, KeyWord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for SubCategory model
    """
    list_display = ('name', 'category', 'slug', 'subcategory_id')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category__name', 'name')
    autocomplete_fields = ('category',)


@admin.register(KeyWord)
class KeyWordAdmin(admin.ModelAdmin):
    """
    Admin interface for KeyWord model
    """
    list_display = ('word', 'slug')
    search_fields = ('word',)
    prepopulated_fields = {'slug': ('word',)}
    ordering = ('word',)