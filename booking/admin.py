from django.contrib import admin
from django.utils.html import format_html
from .models import Table, Booking, Feedback


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "is_vip", "is_active", "image_preview")
    list_filter = ("is_vip", "is_active", "capacity")
    search_fields = ("number", "description")
    readonly_fields = ("image_preview_large",)

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("number", "capacity", "is_vip", "is_active", "description")},
        ),
        (
            "Изображение столика",
            {
                "fields": ("image", "image_preview_large"),
            },
        ),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Фото"

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 400px;" />',
                obj.image.url,
            )
        return "Нет изображения"

    image_preview_large.short_description = "Превью"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "start_time",
        "end_time",
        "user",
        "table",
        "guests_count",
        "status",
    )
    list_filter = ("status", "date", "table")
    search_fields = ("user__email", "table__number")
    date_hierarchy = "date"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    date_hierarchy = "created_at"
