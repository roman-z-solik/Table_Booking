import json
import os
import shutil
from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from booking.models import Table, Booking, Page, Feedback, GalleryImage, MenuItem, TeamMember


class Command(BaseCommand):
    help = "Сохранить все данные и медиа файлы"

    def handle(self, *args, **options):
        if not os.path.exists("data"):
            os.makedirs("data")

        all_data = []

        for model in [Table, Booking, Page, Feedback, GalleryImage, MenuItem, TeamMember]:
            try:
                data = serializers.serialize("json", model.objects.all())
                all_data.append({"model": model.__name__, "data": json.loads(data)})
                print(f"Сохранено: {model.__name__}")
            except Exception as e:
                print(f"Ошибка {model.__name__}: {e}")

        with open("data/data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)

        if hasattr(settings, "MEDIA_ROOT") and os.path.exists(settings.MEDIA_ROOT):
            media_backup = "data/media"
            if os.path.exists(media_backup):
                shutil.rmtree(media_backup)
            shutil.copytree(settings.MEDIA_ROOT, media_backup)
            print(f"Медиа файлы сохранены в {media_backup}")

        print("Все данные сохранены в папке data/")
