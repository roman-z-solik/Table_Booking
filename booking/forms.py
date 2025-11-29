from django import forms
from .models import Feedback
from .models import Table
from .models import Booking
from datetime import date, timedelta
from datetime import datetime


class BookingForm(forms.ModelForm):
    """Форма бронирования столика."""

    duration_hours = forms.ChoiceField(
        choices=[
            (1, '1 час'),
            (2, '2 часа'),
            (3, '3 часа'),
            (4, '4 часа')
        ],
        label='Продолжительность',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    guests_count = forms.ChoiceField(
        choices=[],
        label='Количество гостей',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Booking
        fields = ['table', 'date', 'start_time', 'duration_hours', 'guests_count', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'table': 'Столик',
            'date': 'Дата',
            'start_time': 'Время начала',
            'special_requests': 'Особые пожелания',
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы бронирования."""
        super().__init__(*args, **kwargs)
        self.fields['table'].queryset = Table.objects.filter(is_active=True)
        self.fields['table'].widget.attrs.update({'class': 'form-control'})

        table_id = self.initial.get('table')
        if not table_id and self.data.get('table'):
            table_id = self.data.get('table')

        capacity = 8
        if table_id:
            try:
                table = Table.objects.get(id=table_id)
                capacity = table.capacity
            except (Table.DoesNotExist, ValueError):
                pass

        self.fields['guests_count'].choices = [
            (i, f'{i} {"человек" if i == 1 else "человека" if i < 5 else "человек"}')
            for i in range(1, capacity + 1)
        ]

        today = date.today()
        self.fields['date'].initial = today.strftime('%Y-%m-%d')

        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        self.fields['start_time'].initial = next_hour.strftime('%H:%M')

        from django.conf import settings
        self.fields['start_time'].help_text = f'Ресторан работает с {settings.OPEN_TIME} до {settings.CLOSE_TIME}'

    def clean_guests_count(self):
        """Преобразует guests_count из строки в число."""
        guests_count = self.cleaned_data.get('guests_count')
        if guests_count:
            return int(guests_count)
        return guests_count

    def clean_duration_hours(self):
        """Преобразует duration_hours из строки в число."""
        duration_hours = self.cleaned_data.get('duration_hours')
        if duration_hours:
            return int(duration_hours)
        return duration_hours


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи."""

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'name': 'Ваше имя',
            'email': 'Email',
            'message': 'Сообщение',
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы обратной связи."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            self.fields['email'].initial = self.user.email
            self.fields['name'].initial = f"{self.user.first_name} {self.user.last_name}".strip()
