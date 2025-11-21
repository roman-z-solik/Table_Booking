from django.shortcuts import render


def register(request):
    """Страница регистрации пользователя."""
    return render(request, 'users/register.html')
