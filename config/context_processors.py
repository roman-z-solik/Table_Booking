from django.conf import settings


def restaurant_info(request):
    """Добавляет информацию о ресторане в контекст шаблонов."""
    return {
        "restaurant_name": settings.RESTAURANT_NAME,
        "restaurant_description": settings.RESTAURANT_DESCRIPTION,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_email": settings.CONTACT_EMAIL,
        "address": settings.ADDRESS,
        "open_time": settings.OPEN_TIME,
        "close_time": settings.CLOSE_TIME,
    }
