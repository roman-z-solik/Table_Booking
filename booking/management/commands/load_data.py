# Это дополнительный функционал, никак не связанный с работой, делал для себя, т.к.
# часто работаю из разных мест. Только для тестирования
import json
import os
import shutil
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from django.conf import settings


class Command(BaseCommand):
    help = "Загрузить данные и медиа файлы"

    def handle(self, *args, **options):
        if not os.path.exists("data/data.json"):
            print("Файл data/data.json не найден")
            print("Сначала выполните: python manage.py save_data")
            return

        with open("data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        total_loaded = 0
        total_errors = 0

        for item in data:
            model_name = item["model"]
            records = item["data"]

            print(f"Загрузка {model_name} ({len(records)} записей)")

            for i, record in enumerate(records, 1):
                try:
                    obj = list(deserialize("json", json.dumps([record])))[0]
                    obj.save()
                    total_loaded += 1
                except Exception as e:
                    total_errors += 1
                    print(f"Ошибка записи {i}: {e}")

        media_backup = "data/media"
        if os.path.exists(media_backup):
            if hasattr(settings, "MEDIA_ROOT"):
                if os.path.exists(settings.MEDIA_ROOT):
                    shutil.rmtree(settings.MEDIA_ROOT)
                shutil.copytree(media_backup, settings.MEDIA_ROOT)
                print("Медиа файлы восстановлены")

        print("")
        print("=" * 40)
        print(f"Загружено записей: {total_loaded}")
        print(f"Ошибок: {total_errors}")
        print("=" * 40)
