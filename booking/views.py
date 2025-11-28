from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking, Table
from .forms import BookingForm


def home(request):
    """Главная страница сайта."""
    return render(request, 'booking/home.html')


@login_required
def booking_create(request):
    """Создание нового бронирования."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            try:
                booking.save()
                messages.success(request, 'Столик успешно забронирован!')
                return redirect('booking_list')
            except Exception as e:
                messages.error(request, f'Ошибка бронирования: {str(e)}')
    else:
        form = BookingForm()

    tables = Table.objects.filter(is_active=True)
    return render(request, 'booking/booking_form.html', {
        'form': form,
        'tables': tables
    })


@login_required
def booking_list(request):
    """Список бронирований пользователя."""
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-start_time')
    return render(request, 'booking/booking_list.html', {'bookings': bookings})


@login_required
def booking_cancel(request, booking_id):
    """Отмена бронирования."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'active':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Бронирование отменено.')
    return redirect('booking_list')
