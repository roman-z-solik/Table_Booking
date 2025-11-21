from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class Table(models.Model):
    """Модель столика ресторана."""

    CAPACITY_CHOICES = [
        (2, '2 человека'),
        (4, '4 человека'),
        (6, '6 человек'),
        (8, '8 человек'),
    ]

    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(choices=CAPACITY_CHOICES)
    is_vip = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """Строковое представление столика."""
        return f"Столик №{self.number} ({self.get_capacity_display()})"


class Booking(models.Model):
    """Модель бронирования столика."""

    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.PositiveIntegerField()
    end_time = models.TimeField()
    guests_count = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
        """Строковое представление бронирования."""
        return f"{self.date} {self.start_time} - {self.user.email}"


class Feedback(models.Model):
    """Модель обратной связи от пользователей."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Строковое представление отзыва."""
        return f"{self.name} - {self.created_at}"
    