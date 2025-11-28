from django import forms
from .models import Feedback
from .models import Table
from .models import Booking
from datetime import date, timedelta
from datetime import datetime


class BookingForm(forms.ModelForm):
    """Форма бронирования столика."""

    class Meta:
        model = Booking
        fields = ['table', 'date', 'start_time', 'duration_hours', 'guests_count', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4}),
            'guests_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'table': 'Столик',
            'date': 'Дата',
            'start_time': 'Время начала',
            'duration_hours': 'Продолжительность (часов)',
            'guests_count': 'Количество гостей',
            'special_requests': 'Особые пожелания',
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы бронирования."""
        super().__init__(*args, **kwargs)
        self.fields['table'].queryset = Table.objects.filter(is_active=True)
        self.fields['table'].widget.attrs.update({'class': 'form-control'})

        today = date.today()
        self.fields['date'].initial = today.strftime('%Y-%m-%d')

        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        self.fields['start_time'].initial = next_hour.strftime('%H:%M')

        from django.conf import settings
        self.fields['start_time'].help_text = f'Ресторан работает с {settings.OPEN_TIME} до {settings.CLOSE_TIME}'
        self.fields['duration_hours'].help_text = f'Максимальное время бронирования: {settings.MAX_BOOKING_HOURS} часов'


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
