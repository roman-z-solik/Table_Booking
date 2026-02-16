from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings


@receiver(post_migrate)
def create_restaurant_settings(sender, **kwargs):
    """Создает настройки ресторана из .env после миграций"""
    if sender.name == "booking":
        from .models import RestaurantSettings

        if not RestaurantSettings.objects.exists():
            max_capacity = getattr(settings, "MAX_TABLE_CAPACITY", 12)

            table_capacities = getattr(settings, "TABLE_CAPACITIES", [])
            if table_capacities:
                table_caps = [cap[0] for cap in table_capacities]
            else:
                table_caps = [2, 4, 6, 8, 10, 12]

            booking_statuses = getattr(settings, "BOOKING_STATUSES", [])
            if booking_statuses:
                statuses = [status[0] for status in booking_statuses]
            else:
                statuses = ["active", "cancelled"]

            RestaurantSettings.objects.create(
                max_table_capacity=max_capacity,
                table_capacities=table_caps,
                booking_statuses=statuses,
            )
