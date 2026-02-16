from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomAuthenticationForm

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone="+79991234567",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_str(self):
        self.assertEqual(str(self.user), "testuser@example.com")

    def test_user_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Test User")

    def test_user_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), "Test")


class AuthViewsTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "first_name": "New",
            "last_name": "User",
            "phone": "+79991234567",
        }

    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post(self):
        response = self.client.post(reverse("register"), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login_view_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post_valid(self):
        User.objects.create_user(
            username="loginuser", email="loginuser@example.com", password="testpass123"
        )
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser@example.com", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        _ = User.objects.create_user(  # Переменная не используется
            username="logoutuser",
            email="logoutuser@example.com",
            password="testpass123",
        )
        self.client.login(email="logoutuser@example.com", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            email="profileuser@example.com",
            password="testpass123",
            first_name="Profile",
            last_name="User",
        )

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(email="profileuser@example.com", password="testpass123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_view_requires_login(self):
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_view_logged_in(self):
        self.client.login(email="profileuser@example.com", password="testpass123")
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)


class UserFormsTest(TestCase):
    def test_custom_user_creation_form_valid(self):
        form_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+79991234567",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_authentication_form_valid(self):
        _ = User.objects.create_user(
            username="authuser", email="authuser@example.com", password="testpass123"
        )

        form_data = {"username": "authuser@example.com", "password": "testpass123"}
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())
