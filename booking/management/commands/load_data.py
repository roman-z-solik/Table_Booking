import json
import os
import shutil
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from django.conf import settings
from django.db import transaction
from booking.models import Table, Booking, Page, Feedback, GalleryImage, MenuItem, TeamMember


class Command(BaseCommand):
    help = "Загрузить данные и медиа файлы"

    def handle(self, *args, **options):
        if not os.path.exists("data/data.json"):
            self.stdout.write("Файл data/data.json не найден")
            self.stdout.write("Сначала выполните: python manage.py save_data")
            return

        with open("data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        total_loaded = 0
        total_errors = 0

        model_map = {
            "Table": Table,
            "Booking": Booking,
            "Page": Page,
            "Feedback": Feedback,
            "GalleryImage": GalleryImage,
            "MenuItem": MenuItem,
            "TeamMember": TeamMember,
        }

        with transaction.atomic():
            for item in data:
                model_name = item["model"]
                records = item["data"]

                self.stdout.write(f"Загрузка {model_name} ({len(records)} записей)")

                for i, record in enumerate(records, 1):
                    try:
                        natural_key = record.get("pk")
                        record["pk"] = None

                        obj = list(deserialize("json", json.dumps([record])))[0]

                        obj.object.pk = None

                        obj.save(using="default")
                        total_loaded += 1

                        if i % 100 == 0:
                            self.stdout.write(f"  Загружено {i} записей...")

                    except Exception as e:
                        total_errors += 1
                        self.stderr.write(f"Ошибка записи {i}: {e}")

        media_backup = "data/media"
        if os.path.exists(media_backup):
            if hasattr(settings, "MEDIA_ROOT"):
                if os.path.exists(settings.MEDIA_ROOT):
                    shutil.rmtree(settings.MEDIA_ROOT)
                shutil.copytree(media_backup, settings.MEDIA_ROOT)
                self.stdout.write("Медиа файлы восстановлены")

        self.stdout.write("")
        self.stdout.write("=" * 40)
        self.stdout.write(f"Загружено записей: {total_loaded}")
        self.stdout.write(f"Ошибок: {total_errors}")
        self.stdout.write("=" * 40)
