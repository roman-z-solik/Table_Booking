from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Feedback, Table, Booking
from datetime import date, timedelta, datetime


class BookingForm(forms.ModelForm):
    """Форма создания бронирования"""

    duration_hours = forms.ChoiceField(
        choices=[(i, f"{i} час" if i == 1 else f"{i} часа" if i < 5 else f"{i} часов")
                 for i in range(1, settings.MAX_BOOKING_HOURS + 1)],
        label="Продолжительность",
        widget=forms.Select(attrs={"class": "form-control", "id": "id_duration"}),
    )

    guests_count = forms.ChoiceField(
        label="Количество гостей",
        widget=forms.Select(attrs={"class": "form-control", "id": "id_guests"}),
        choices=[(1, "1 чел.")]
    )

    start_time = forms.ChoiceField(
        label="Время начала",
        widget=forms.Select(attrs={"class": "form-control", "id": "id_start_time"}),
        choices=[]
    )

    class Meta:
        model = Booking
        fields = [
            "table",
            "date",
            "duration_hours",
            "guests_count",
            "start_time",
            "special_requests",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control", "id": "id_date"}),
            "special_requests": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "table": forms.Select(attrs={"class": "form-control", "id": "id_table"}),
        }
        labels = {
            "table": "Столик",
            "date": "Дата",
            "special_requests": "Специальные пожелания",
        }

    def __init__(self, *args, **kwargs):
        table_id = kwargs.pop('table_id', None)
        super().__init__(*args, **kwargs)

        self.fields["table"].queryset = Table.objects.filter(is_active=True)

        table = None
        if table_id:
            try:
                table = Table.objects.get(id=table_id)
                self.fields["table"].initial = table
                self.fields["table"].disabled = True
            except Table.DoesNotExist:
                pass

        if not table and 'table' in self.initial and self.initial['table']:
            try:
                table = Table.objects.get(id=self.initial['table'])
            except (Table.DoesNotExist, ValueError):
                pass

        if table:
            guest_choices = [(i, f"{i} чел.") for i in range(1, table.capacity + 1)]
            self.fields["guests_count"].choices = guest_choices

        if not self.fields["date"].initial:
            today = date.today()
            self.fields["date"].initial = today.strftime("%Y-%m-%d")

        try:
            open_time = datetime.strptime(settings.OPEN_TIME, "%H:%M").time()
            close_time = datetime.strptime(settings.CLOSE_TIME, "%H:%M").time()

            time_choices = []
            current_hour = open_time.hour

            while current_hour < close_time.hour:
                time_str = f"{current_hour:02d}:00"
                time_choices.append((time_str, time_str))
                current_hour += 1

            self.fields["start_time"].choices = time_choices

        except ValueError:
            self.fields["start_time"].widget = forms.TimeInput(
                attrs={"type": "time", "class": "form-control", "id": "id_start_time"}
            )

        self.fields[
            "date"].help_text = f"Максимально можно забронировать на {settings.MAX_BOOKING_DAYS_AHEAD} дней вперед"

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get("table")
        date_obj = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        duration_hours = cleaned_data.get("duration_hours")
        guests_count = cleaned_data.get("guests_count")

        if all([table, date_obj, start_time, duration_hours, guests_count]):
            try:
                duration = int(duration_hours)
                guests = int(guests_count)
                start_time_obj = start_time

                open_time = datetime.strptime(settings.OPEN_TIME, "%H:%M").time()
                close_time = datetime.strptime(settings.CLOSE_TIME, "%H:%M").time()

                start_datetime = datetime.combine(date_obj, start_time_obj)
                end_datetime = start_datetime + timedelta(hours=duration)
                end_time_obj = end_datetime.time()

                now = datetime.now()

                if date_obj == now.date():
                    if start_datetime < now + timedelta(hours=1):
                        self.add_error(
                            "start_time",
                            "Бронь должна быть минимум на 1 час позже текущего времени"
                        )

                if start_time_obj < open_time:
                    self.add_error(
                        "start_time",
                        f"Ресторан открывается в {settings.OPEN_TIME}"
                    )

                end_date = date_obj
                if end_time_obj < start_time_obj:
                    end_date = date_obj + timedelta(days=1)

                if end_date > date_obj:
                    self.add_error(
                        "duration_hours",
                        f"Бронь не может переходить на следующий день"
                    )
                    raise ValidationError("")
                elif end_time_obj > close_time:
                    self.add_error(
                        "duration_hours",
                        f"Бронь завершится в {end_time_obj.strftime('%H:%M')}, но ресторан закрывается в {settings.CLOSE_TIME}"
                    )
                    raise ValidationError("")

                if table and not table.is_available(date_obj, start_time_obj, duration):
                    busy_times = table.get_busy_times(date_obj)
                    self.add_error(
                        "start_time",
                        f"Столик занят на выбранное время. Занятое время: {', '.join(busy_times)}"
                    )

                max_future_date = now.date() + timedelta(days=settings.MAX_BOOKING_DAYS_AHEAD)
                if date_obj > max_future_date:
                    self.add_error(
                        "date",
                        f"Можно бронировать максимум на {settings.MAX_BOOKING_DAYS_AHEAD} дней вперед"
                    )

            except ValueError as e:
                self.add_error(None, f"Ошибка обработки данных: {str(e)}")

        if table and guests_count:
            try:
                guests = int(guests_count)
                if guests > table.capacity:
                    self.add_error(
                        "guests_count",
                        f"Этот столик вмещает максимум {table.capacity} гостей"
                    )
            except ValueError:
                pass

    def clean_date(self):
        date_obj = self.cleaned_data.get("date")
        if date_obj and date_obj < date.today():
            raise ValidationError("Нельзя бронировать на прошедшую дату")
        return date_obj

    def clean_guests_count(self):
        guests_count = self.cleaned_data.get("guests_count")
        if guests_count:
            try:
                guests = int(guests_count)
                if guests < 1:
                    raise ValidationError("Количество гостей должно быть не менее 1")
                return guests
            except ValueError:
                raise ValidationError("Некорректное количество гостей")
        return guests_count

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")
        if start_time:
            try:
                return datetime.strptime(start_time, "%H:%M").time()
            except ValueError:
                raise ValidationError("Некорректный формат времени")
        return start_time


class BookingEditForm(BookingForm):
    """Форма редактирования бронирования"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            table = self.instance.table
            guest_choices = [(i, f"{i} чел.") for i in range(1, table.capacity + 1)]
            self.fields["guests_count"].choices = guest_choices
            self.fields["guests_count"].initial = self.instance.guests_count

            self.fields["duration_hours"].initial = self.instance.duration_hours

            self.fields["start_time"].initial = self.instance.start_time.strftime("%H:%M")

            date_str = self.instance.date.strftime("%Y-%m-%d")
            self.fields["date"].initial = date_str
            self.initial['date'] = date_str

    def clean(self):
        cleaned_data = super(forms.ModelForm, self).clean()

        table = cleaned_data.get("table")
        date_obj = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        duration_hours = cleaned_data.get("duration_hours")
        guests_count = cleaned_data.get("guests_count")

        if all([table, date_obj, start_time, duration_hours, guests_count]):
            try:
                duration = int(duration_hours)
                guests = int(guests_count)
                start_time_obj = start_time

                open_time = datetime.strptime(settings.OPEN_TIME, "%H:%M").time()
                close_time = datetime.strptime(settings.CLOSE_TIME, "%H:%M").time()

                start_datetime = datetime.combine(date_obj, start_time_obj)
                end_datetime = start_datetime + timedelta(hours=duration)
                end_time_obj = end_datetime.time()

                now = datetime.now()

                if date_obj == now.date():
                    if start_datetime < now + timedelta(hours=1):
                        self.add_error(
                            "start_time",
                            "Бронь должна быть минимум на 1 час позже текущего времени"
                        )

                if start_time_obj < open_time:
                    self.add_error(
                        "start_time",
                        f"Ресторан открывается в {settings.OPEN_TIME}"
                    )

                end_date = date_obj
                if end_time_obj < start_time_obj:
                    end_date = date_obj + timedelta(days=1)

                if end_date > date_obj:
                    self.add_error(
                        "duration_hours",
                        f"Бронь не может переходить на следующий день"
                    )
                    raise ValidationError("")
                elif end_time_obj > close_time:
                    self.add_error(
                        "duration_hours",
                        f"Бронь завершится в {end_time_obj.strftime('%H:%M')}, но ресторан закрывается в {settings.CLOSE_TIME}"
                    )
                    raise ValidationError("")

                if table and not table.is_available(date_obj, start_time_obj, duration,
                                                    exclude_booking_id=self.instance.id):
                    busy_times = table.get_busy_times(date_obj)
                    busy_times_filtered = []
                    for busy in busy_times:
                        start_str, end_str = busy.split('-')
                        if not (start_str == self.instance.start_time.strftime(
                                '%H:%M') and end_str == self.instance.end_time.strftime('%H:%M')):
                            busy_times_filtered.append(busy)

                    if busy_times_filtered:
                        self.add_error(
                            "start_time",
                            f"Столик занят на выбранное время. Занятое время: {', '.join(busy_times_filtered)}"
                        )

                max_future_date = now.date() + timedelta(days=settings.MAX_BOOKING_DAYS_AHEAD)
                if date_obj > max_future_date:
                    self.add_error(
                        "date",
                        f"Можно бронировать максимум на {settings.MAX_BOOKING_DAYS_AHEAD} дней вперед"
                    )

            except ValueError as e:
                self.add_error(None, f"Ошибка обработки данных: {str(e)}")

        if table and guests_count:
            try:
                guests = int(guests_count)
                if guests > table.capacity:
                    self.add_error(
                        "guests_count",
                        f"Этот столик вмещает максимум {table.capacity} гостей"
                    )
            except ValueError:
                pass

        return cleaned_data


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
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            self.fields["email"].initial = self.user.email
            self.fields["name"].initial = (
                f"{self.user.first_name} {self.user.last_name}".strip()
            )
