from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .forms import CustomUserChangeForm
from booking.utils import send_registration_email
from django.conf import settings


def register(request):
    """Регистрация нового пользователя."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            try:
                send_registration_email(
                    user,
                    f"Добро пожаловать в {settings.RESTAURANT_NAME}!",
                    "emails/registration.html",
                )
                messages.success(request, "Вы зарегистрированы. Проверьте Вашу почту.")
            except Exception as e:
                messages.warning(
                    request, f"Ваша регистрация прошла, но почта недоступна: {e}"
                )

            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    """Вход пользователя."""
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {user.first_name}!")
                return redirect("home")
            else:
                messages.error(request, "Неверный email или пароль.")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomAuthenticationForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def user_logout(request):
    """Выход пользователя."""
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")
    return redirect("home")


@login_required
def profile(request):
    """Профиль пользователя."""
    return render(request, "users/profile.html", {"user": request.user})


@login_required
def profile_edit(request):
    """Редактирование профиля пользователя."""
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("profile")
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def profile_delete(request):
    """Удаление аккаунта пользователя."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Ваш аккаунт был удален.")
        return redirect("home")

    return render(request, "users/profile_delete.html")
