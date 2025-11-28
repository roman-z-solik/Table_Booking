from django.contrib import admin
from .models import Table, Booking, Feedback


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """Админ-панель для управления столиками."""

    list_display = ("number", "capacity", "is_vip", "is_active")
    list_filter = ("is_vip", "is_active", "capacity")
    search_fields = ("number", "description")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Админ-панель для управления бронированиями."""

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
    """Админ-панель для управления отзывами."""

    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "message")
    date_hierarchy = "created_at"
