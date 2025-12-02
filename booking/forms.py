from django import forms
from django.conf import settings
from .models import Feedback, Table, Booking
from datetime import date, timedelta
from datetime import datetime


class BookingForm(forms.ModelForm):
    """Форма бронирования столика"""

    duration_hours = forms.ChoiceField(
        choices=[(1, "1 час"), (2, "2 часа"), (3, "3 часа"), (4, "4 часа")],
        label="Продолжительность",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    guests_count = forms.ChoiceField(
        choices=[],
        label="Количество гостей",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Booking
        fields = [
            "table",
            "date",
            "start_time",
            "duration_hours",
            "guests_count",
            "special_requests",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "special_requests": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "table": forms.Select(attrs={"class": "form-control", "id": "id_table"}),
        }
        labels = {
            "table": "Столик",
            "date": "Дата",
            "start_time": "Время начала",
            "special_requests": "Специальные пожелания",
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы"""
        super().__init__(*args, **kwargs)

        max_capacity = settings.MAX_TABLE_CAPACITY

        self.fields["table"].queryset = Table.objects.filter(is_active=True)

        table_id = self.initial.get("table")
        if not table_id and hasattr(self, "data") and self.data.get("table"):
            table_id = self.data.get("table")

        capacity = max_capacity
        selected_table = None

        if table_id:
            try:
                selected_table = Table.objects.get(id=table_id)
                capacity = selected_table.capacity
                self.initial["table"] = selected_table
            except (Table.DoesNotExist, ValueError):
                pass

        self.fields["guests_count"].choices = [
            (i, f'{i} {"человек" if i == 1 else "человека" if i < 5 else "человек"}')
            for i in range(1, capacity + 1)
        ]

        self.selected_table = selected_table

        today = date.today()
        self.fields["date"].initial = today.strftime("%Y-%m-%d")

        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(
            minute=0, second=0, microsecond=0
        )
        self.fields["start_time"].initial = next_hour.strftime("%H:%M")

        self.fields["start_time"].help_text = (
            f"Ресторан работает с {settings.OPEN_TIME} до {settings.CLOSE_TIME}"
        )

    def clean(self):
        """Валидация времени бронирования"""
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        duration_hours = cleaned_data.get("duration_hours")
        date_obj = cleaned_data.get("date")

        if start_time and duration_hours and date_obj:
            open_time = datetime.strptime(settings.OPEN_TIME, "%H:%M").time()
            close_time = datetime.strptime(settings.CLOSE_TIME, "%H:%M").time()

            if start_time < open_time:
                self.add_error(
                    "start_time", f"Ресторан открывается в {settings.OPEN_TIME}"
                )

            end_datetime = datetime.combine(date_obj, start_time) + timedelta(
                hours=duration_hours
            )
            end_time = end_datetime.time()

            if end_time < start_time:
                self.add_error(
                    "duration_hours",
                    f"Нельзя бронировать столик после {settings.CLOSE_TIME}",
                )

            elif end_time > close_time:
                self.add_error(
                    "duration_hours",
                    f"Бронирование должно завершиться до {settings.CLOSE_TIME}",
                )

        return cleaned_data

    def clean_guests_count(self):
        """Преобразование количества гостей"""
        guests_count = self.cleaned_data.get("guests_count")
        if guests_count:
            return int(guests_count)
        return guests_count

    def clean_duration_hours(self):
        """Преобразование длительности"""
        duration_hours = self.cleaned_data.get("duration_hours")
        if duration_hours:
            return int(duration_hours)
        return duration_hours


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи"""

    class Meta:
        model = Feedback
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "readonly": "readonly"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "readonly": "readonly"}
            ),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
        labels = {
            "name": "Ваше имя",
            "email": "Email",
            "message": "Сообщение",
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы"""
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            self.fields["email"].initial = self.user.email
            self.fields["name"].initial = (
                f"{self.user.first_name} {self.user.last_name}".strip()
            )
