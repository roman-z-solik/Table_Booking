from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Table
from .forms import BookingForm, FeedbackForm
from .utils import send_booking_email


def home(request):
    """Главная страница сайта."""
    return render(request, "booking/home.html")


def about(request):
    """Страница о ресторане."""
    return render(request, "booking/about.html")


def feedback(request):
    """Форма обратной связи."""
    if request.method == "POST":
        form = FeedbackForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.",
            )
            return redirect("home")
    else:
        form = FeedbackForm(user=request.user)

    return render(request, "booking/feedback.html", {"form": form})


@login_required
def booking_create(request):
    """Создание нового бронирования."""
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            if not booking.table.is_available(
                booking.date, booking.start_time, booking.duration_hours
            ):
                busy_times = booking.table.get_busy_times(booking.date)
                messages.error(
                    request,
                    f'Столик занят на выбранное время. Занятое время: {", ".join(busy_times)}',
                )
                return render(request, "booking/booking_form.html", {"form": form})

            try:
                booking.save()

                try:
                    send_booking_email(
                        request.user,
                        booking,
                        "Подтверждение бронирования",
                        "emails/booking_confirmation.html",
                    )
                except Exception as e:
                    print(f"Ошибка отправки email: {e}")

                messages.success(request, "Столик успешно забронирован!")
                return redirect("booking_list")
            except Exception as e:
                messages.error(request, f"Ошибка бронирования: {str(e)}")
    else:
        form = BookingForm()

        table_id = request.GET.get("table_id")
        if table_id:
            form.fields["table"].initial = table_id

    tables = Table.objects.filter(is_active=True)

    table_info = None
    if request.GET.get("table_id") and request.GET.get("date"):
        try:
            table = Table.objects.get(id=request.GET.get("table_id"))
            date_str = request.GET.get("date")
            busy_times = table.get_busy_times(date_str)
            table_info = {"table": table, "date": date_str, "busy_times": busy_times}
        except Table.DoesNotExist:
            pass

    return render(
        request,
        "booking/booking_form.html",
        {"form": form, "tables": tables, "table_info": table_info},
    )


@login_required
def booking_list(request):
    """Список бронирований пользователя."""
    bookings = Booking.objects.filter(user=request.user).order_by(
        "-date", "-start_time"
    )
    return render(request, "booking/booking_list.html", {"bookings": bookings})


@login_required
def booking_cancel(request, booking_id):
    """Отмена бронирования."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == "active":
        booking.status = "cancelled"
        booking.save()

        try:
            send_booking_email(
                request.user,
                booking,
                "Отмена бронирования",
                "emails/booking_cancellation.html",
            )
        except Exception as e:
            print(f"Ошибка отправки email: {e}")

        messages.success(request, "Бронирование отменено.")
    return redirect("booking_list")
