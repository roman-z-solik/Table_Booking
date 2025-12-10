from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta

User = get_user_model()


class Table(models.Model):
    """Модель столика ресторана"""
    number = models.IntegerField(unique=True, verbose_name="Номер столика")
    capacity = models.IntegerField(
        verbose_name="Вместимость",
        validators=[MinValueValidator(1)],
        help_text="Максимальное количество гостей"
    )
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
        return f"Столик №{self.number} ({self.capacity} чел.)"

    def get_busy_times(self, date):
        """Возвращает список занятых временных слотов"""
        bookings = Booking.objects.filter(table=self, date=date).order_by("start_time")

        busy_times = []
        for booking in bookings:
            start_time = booking.start_time.strftime("%H:%M")
            end_time = booking.end_time.strftime("%H:%M")
            busy_times.append(f"{start_time}-{end_time}")

        return busy_times

    def is_available(self, date, start_time, duration_hours, exclude_booking_id=None):
        """Проверяет доступность столика в указанное время"""
        end_time = (
            datetime.combine(date, start_time) + timedelta(hours=duration_hours)
        ).time()

        conflicting_bookings = Booking.objects.filter(table=self, date=date).filter(
            start_time__lt=end_time, end_time__gt=start_time
        )

        if exclude_booking_id:
            conflicting_bookings = conflicting_bookings.exclude(id=exclude_booking_id)

        return not conflicting_bookings.exists()


class Booking(models.Model):
    """Модель бронирования столика"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Столик")
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    guests_count = models.IntegerField(verbose_name="Количество гостей")
    special_requests = models.TextField(
        blank=True, null=True, verbose_name="Специальные пожелания"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"Бронирование #{self.id}"

    @property
    def duration_hours(self):
        """Продолжительность бронирования в часах"""
        if self.start_time and self.end_time:
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            if end < start:
                end += timedelta(days=1)
            duration = end - start
            return duration.seconds // 3600
        return 0


class Feedback(models.Model):
    """Модель отзыва о ресторане"""
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


class Page(models.Model):
    """Модель для страниц сайта"""
    PAGE_TYPES = [
        ("about", "О нас"),
        ("gallery", "Галерея"),
        ("menu", "Блюда"),
        ("team", "Команда"),
        ("contacts", "Контакты"),
    ]

    page_type = models.CharField(
        max_length=20, choices=PAGE_TYPES, unique=True, verbose_name="Тип страницы"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="Подзаголовок")
    main_image = models.ImageField(
        upload_to="pages/", blank=True, null=True, verbose_name="Главное фото"
    )
    content = models.TextField(verbose_name="Содержимое")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["order", "title"]

    def __str__(self):
        return f"{self.get_page_type_display()} - {self.title}"


class GalleryImage(models.Model):
    """Изображения для галереи"""
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="Страница",
    )
    image = models.ImageField(upload_to="gallery/", verbose_name="Изображение")
    title = models.CharField(max_length=100, blank=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Изображение галереи"
        verbose_name_plural = "Изображения галереи"
        ordering = ["order", "-uploaded_at"]

    def __str__(self):
        return self.title or f"Изображение {self.id}"


class MenuItem(models.Model):
    """Позиции меню"""
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="Страница",
    )
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(
        upload_to="menu/", blank=True, null=True, verbose_name="Фото"
    )
    category = models.CharField(max_length=50, blank=True, verbose_name="Категория")
    is_special = models.BooleanField(
        default=False, verbose_name="Специальное предложение"
    )
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Позиция меню"
        verbose_name_plural = "Позиции меню"
        ordering = ["category", "order", "name"]

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class TeamMember(models.Model):
    """Члены команды"""
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="team_members",
        verbose_name="Страница",
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    position = models.CharField(max_length=100, verbose_name="Должность")
    bio = models.TextField(verbose_name="Биография")
    photo = models.ImageField(
        upload_to="team/", blank=True, null=True, verbose_name="Фото"
    )
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Член команды"
        verbose_name_plural = "Члены команды"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} - {self.position}"
