from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from .models import Booking, Table, Page
from .forms import BookingForm, FeedbackForm
from datetime import datetime, timedelta


def home(request):
    """Главная страница со столиками"""
    tables = Table.objects.filter(is_active=True)

    table_status = []
    today = timezone.now().date()

    for table in tables:
        bookings_today = Booking.objects.filter(table=table, date=today).order_by(
            "start_time"
        )
        busy_times = []

        for booking in bookings_today:
            busy_times.append(
                f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"
            )

        table_status.append(
            {
                "table": table,
                "busy_times": busy_times,
                "has_bookings_today": bookings_today.exists(),
                "bookings_count": bookings_today.count(),
            }
        )

    return render(request, "booking/home.html", {"table_status": table_status})


def page_detail(request, page_type):
    """Отображение страницы по типу"""
    try:
        page = Page.objects.get(page_type=page_type, is_active=True)

        context = {
            "page": page,
        }

        if page.page_type == "gallery":
            context["gallery_images"] = page.gallery_images.all()
        elif page.page_type == "menu":
            context["menu_items"] = page.menu_items.all()
        elif page.page_type == "team":
            context["team_members"] = page.team_members.all()

        template_name = f"booking/{page_type}.html"
        return render(request, template_name, context)

    except Page.DoesNotExist:
        return render(
            request,
            "booking/page_under_construction.html",
            {
                "page_type": page_type,
                "page_title": dict(Page.PAGE_TYPES).get(page_type, "Страница"),
            },
        )


def feedback(request):
    """Обработка обратной связи"""
    if request.method == "POST":
        form = FeedbackForm(request.POST, user=request.user)
        if form.is_valid():
            feedback_obj = form.save(commit=False)
            if request.user.is_authenticated:
                feedback_obj.name = (
                    f"{request.user.first_name} {request.user.last_name}".strip()
                )
                feedback_obj.email = request.user.email
            feedback_obj.save()
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
    """Создание бронирования"""
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            duration_hours = form.cleaned_data["duration_hours"]
            start_datetime = datetime.combine(booking.date, booking.start_time)
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            booking.end_time = end_datetime.time()

            if not booking.table.is_available(
                booking.date, booking.start_time, duration_hours
            ):
                busy_times = booking.table.get_busy_times(booking.date)
                messages.error(
                    request,
                    f'Столик занят на выбранное время. Занятое время: {", ".join(busy_times)}',
                )
                return render(request, "booking/booking_form.html", {"form": form})

            booking.save()
            messages.success(request, "Столик успешно забронирован!")
            return redirect("booking_list")
    else:
        table_id = request.GET.get("table_id")
        booking_date = request.GET.get("date")

        initial_data = {}
        if table_id:
            initial_data["table"] = table_id
        if booking_date:
            initial_data["date"] = booking_date

        form = BookingForm(initial=initial_data)

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

    selected_table = None
    if request.GET.get("table_id"):
        try:
            selected_table = Table.objects.get(id=request.GET.get("table_id"))
        except Table.DoesNotExist:
            selected_table = None

    return render(
        request,
        "booking/booking_form.html",
        {
            "form": form,
            "tables": tables,
            "table_info": table_info,
            "selected_table": selected_table,
        },
    )


@login_required
def booking_list(request):
    """Список бронирований пользователя"""
    bookings = Booking.objects.filter(user=request.user).order_by(
        "-date", "-start_time"
    )

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "booking/booking_list.html",
        {"page_obj": page_obj, "bookings": page_obj.object_list},
    )


@login_required
def booking_cancel(request, booking_id):
    """Отмена бронирования"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        booking.delete()
        messages.success(request, "Бронирование отменено.")
        return redirect("booking_list")

    return render(request, "booking/booking_cancel.html", {"booking": booking})


def get_table_capacity(request, table_id):
    """API: получение вместимости столика"""
    try:
        table = Table.objects.get(id=table_id, is_active=True)
        return JsonResponse({"capacity": table.capacity, "table_number": table.number})
    except Table.DoesNotExist:
        return JsonResponse(
            {"capacity": settings.MAX_TABLE_CAPACITY, "table_number": 0}, status=404
        )
