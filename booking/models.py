from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta

User = get_user_model()


class Table(models.Model):
    number = models.IntegerField(unique=True, verbose_name="Номер столика")
    capacity = models.IntegerField(verbose_name="Вместимость")
    is_vip = models.BooleanField(default=False, verbose_name="VIP")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(
        upload_to="tables/", blank=True, null=True, verbose_name="Изображение"
    )

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"

    def __str__(self):
        return f"Столик №{self.number}"

    def get_capacity_display(self):
        capacities = dict(settings.TABLE_CAPACITIES)
        return capacities.get(self.capacity, "Неизвестно")

    def get_busy_times(self, date):
        bookings = Booking.objects.filter(table=self, date=date, status="active")

        busy_times = []
        for booking in bookings:
            start_time = booking.start_time.strftime("%H:%M")
            end_time = booking.end_time.strftime("%H:%M")
            busy_times.append(f"{start_time}-{end_time}")

        return busy_times

    def is_available(self, date, start_time, duration_hours):
        end_time = (
            datetime.combine(date, start_time) + timedelta(hours=duration_hours)
        ).time()

        conflicting_bookings = Booking.objects.filter(
            table=self, date=date, status="active"
        ).filter(start_time__lt=end_time, end_time__gt=start_time)

        return not conflicting_bookings.exists()


class Booking(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Столик")
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    guests_count = models.IntegerField(verbose_name="Количество гостей")
    status = models.CharField(max_length=20, default="active", verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"Бронирование #{self.id}"


class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.name}"
