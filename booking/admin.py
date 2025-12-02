from django.contrib import admin
from .models import (
    Table,
    Booking,
    Feedback,
    RestaurantSettings,
    Page,
    GalleryImage,
    MenuItem,
    TeamMember,
)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ["number", "capacity", "is_vip", "is_active"]
    list_filter = ["is_vip", "is_active"]
    search_fields = ["number", "description"]
    list_editable = ["is_active"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "table",
        "date",
        "start_time",
        "end_time",
        "guests_count",
    ]
    list_filter = ["date", "table"]
    search_fields = ["user__email", "table__number"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["created_at"]


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    list_display = ["max_table_capacity"]

    def has_add_permission(self, request):
        """Запрещаем создавать более одной записи"""
        return not RestaurantSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление единственной записи"""
        return False


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ["image", "title", "description", "order"]


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = [
        "name",
        "description",
        "price",
        "image",
        "category",
        "is_special",
        "order",
    ]


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ["name", "position", "bio", "photo", "order"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "page_type", "is_active", "order", "updated_at"]
    list_filter = ["page_type", "is_active"]
    list_editable = ["is_active", "order"]
    search_fields = ["title", "content"]

    def get_inline_instances(self, request, obj=None):
        """Показываем только нужные inline в зависимости от типа страницы"""
        if not obj:
            return []

        inlines = []
        if obj.page_type == "gallery":
            inlines.append(GalleryImageInline(self.model, self.admin_site))
        elif obj.page_type == "menu":
            inlines.append(MenuItemInline(self.model, self.admin_site))
        elif obj.page_type == "team":
            inlines.append(TeamMemberInline(self.model, self.admin_site))

        return inlines
