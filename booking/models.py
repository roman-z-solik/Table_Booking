from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class Table(models.Model):
    CAPACITY_CHOICES = [
        (2, '2 человека'),
        (4, '4 человека'),
        (6, '6 человек'),
        (8, '8 человек'),
    ]

    number = models.PositiveIntegerField(unique=True, verbose_name='Номер столика')
    capacity = models.PositiveIntegerField(choices=CAPACITY_CHOICES, verbose_name='Вместимость')
    is_vip = models.BooleanField(default=False, verbose_name='VIP столик')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'

    def __str__(self):
        return f"Столик №{self.number} ({self.get_capacity_display()})"

    def is_available(self, date, start_time, duration_hours):
        """Проверка доступности столика на указанное время."""
        start_datetime = datetime.combine(date, start_time)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        end_time = end_datetime.time()

        conflicting_bookings = Booking.objects.filter(
            table=self,
            date=date,
            status='active'
        ).exclude(
            start_time__gte=end_time,
            end_time__lte=start_time
        )

        return not conflicting_bookings.exists()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name='Столик')
    date = models.DateField(verbose_name='Дата')
    start_time = models.TimeField(verbose_name='Время начала')
    duration_hours = models.PositiveIntegerField(verbose_name='Продолжительность (часов)')
    end_time = models.TimeField(verbose_name='Время окончания')
    guests_count = models.PositiveIntegerField(verbose_name='Количество гостей')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    special_requests = models.TextField(blank=True, verbose_name='Особые пожелания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def clean(self):
        """Валидация данных бронирования перед сохранением."""
        errors = {}

        if self.guests_count > self.table.capacity:
            errors['guests_count'] = f'Столик вмещает до {self.table.capacity} гостей'

        if self.guests_count < 1:
            errors['guests_count'] = 'Минимум 1 гость'

        booking_datetime = datetime.combine(self.date, self.start_time)
        if booking_datetime < datetime.now():
            errors['date'] = 'Нельзя бронировать на прошедшее время'

        if self.duration_hours < 1:
            errors['duration_hours'] = 'Минимум 1 час'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Сохранение бронирования с вычислением времени окончания."""
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + timedelta(hours=self.duration_hours)
        self.end_time = end_datetime.time()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} {self.start_time} - {self.user.email}"


class Feedback(models.Model):
    """Модель обратной связи от пользователей."""

    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'

    def __str__(self):
        return f"{self.name} - {self.created_at}"
