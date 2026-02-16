from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_booking_email(user, booking, subject, template):
    """Отправка email о бронировании."""
    html_message = render_to_string(
        template,
        {
            "user": user,
            "booking": booking,
            "restaurant_name": settings.RESTAURANT_NAME,
            "contact_phone": settings.CONTACT_PHONE,
            "contact_email": settings.CONTACT_EMAIL,
            "address": settings.ADDRESS,
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        None,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_registration_email(user, subject, template):
    """Отправка email при регистрации."""
    html_message = render_to_string(
        template,
        {
            "user": user,
            "restaurant_name": settings.RESTAURANT_NAME,
            "contact_phone": settings.CONTACT_PHONE,
            "contact_email": settings.CONTACT_EMAIL,
            "address": settings.ADDRESS,
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        None,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
