from django import forms
from .models import Booking, Table
from datetime import date, timedelta
from .models import Feedback


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
        super().__init__(*args, **kwargs)
        self.fields['table'].queryset = Table.objects.filter(is_active=True)
        self.fields['table'].widget.attrs.update({'class': 'form-control'})
        self.fields['date'].initial = date.today() + timedelta(days=1)


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи."""

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'name': 'Ваше имя',
            'email': 'Email',
            'phone': 'Телефон',
            'message': 'Сообщение',
        }
