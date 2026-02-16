from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Table, Booking, Page
from datetime import date, timedelta, time

User = get_user_model()


class TableModelTest(TestCase):
    def setUp(self):
        self.table = Table.objects.create(
            number=1, capacity=4, is_vip=False, is_active=True, description="Test table"
        )

    def test_table_creation(self):
        self.assertEqual(self.table.number, 1)
        self.assertEqual(self.table.capacity, 4)
        self.assertTrue(self.table.is_active)

    def test_table_str(self):
        self.assertEqual(str(self.table), "Столик №1")

    def test_get_busy_times(self):
        tomorrow = date.today() + timedelta(days=1)
        Booking.objects.create(
            table=self.table,
            user=User.objects.create_user(
                username="testuser1", email="test1@example.com", password="testpass123"
            ),
            date=tomorrow,
            start_time=time(12, 0),
            end_time=time(14, 0),
            guests_count=2,
        )

        busy_times = self.table.get_busy_times(tomorrow)
        self.assertEqual(len(busy_times), 1)
        self.assertIn("12:00-14:00", busy_times[0])


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.table = Table.objects.create(number=2, capacity=2, is_active=True)
        self.booking = Booking.objects.create(
            user=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            start_time=time(12, 0, 0),
            end_time=time(14, 0, 0),
            guests_count=2,
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.table, self.table)
        self.assertEqual(self.booking.guests_count, 2)

    def test_booking_duration_hours(self):
        self.assertEqual(self.booking.duration_hours, 2)


class PageModelTest(TestCase):
    def setUp(self):
        self.page = Page.objects.create(
            page_type="about", title="О нас", content="Test content", is_active=True
        )

    def test_page_creation(self):
        self.assertEqual(self.page.page_type, "about")
        self.assertEqual(self.page.title, "О нас")
        self.assertTrue(self.page.is_active)


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user123",
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.table = Table.objects.create(number=3, capacity=4, is_active=True)
        # Страница about для тестирования
        Page.objects.get_or_create(
            page_type="about",
            defaults={"title": "О нас", "content": "Test content", "is_active": True},
        )

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "booking/home.html")

    def test_about_view(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_feedback_view_get(self):
        response = self.client.get(reverse("feedback"))
        self.assertEqual(response.status_code, 200)

    def test_feedback_view_post_anonymous(self):
        response = self.client.post(
            reverse("feedback"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test message",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_feedback_view_post_authenticated(self):
        self.client.login(email="user@example.com", password="testpass123")
        response = self.client.post(
            reverse("feedback"),
            {
                "name": "John Doe",
                "email": "user@example.com",
                "message": "Test message",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_booking_create_view_login_required(self):
        response = self.client.get(reverse("booking_create"))
        self.assertEqual(response.status_code, 302)

    def test_booking_create_view_logged_in(self):
        self.client.login(email="user@example.com", password="testpass123")
        response = self.client.get(reverse("booking_create"))
        self.assertEqual(response.status_code, 200)

    def test_booking_list_view_login_required(self):
        response = self.client.get(reverse("booking_list"))
        self.assertEqual(response.status_code, 302)

    def test_booking_list_view_logged_in(self):
        self.client.login(email="user@example.com", password="testpass123")
        response = self.client.get(reverse("booking_list"))
        self.assertEqual(response.status_code, 200)

    def test_table_capacity_api(self):
        response = self.client.get(reverse("table_capacity", args=[self.table.id]))
        self.assertEqual(response.status_code, 200)


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.table = Table.objects.create(number=5, capacity=6, is_active=True)
        self.tomorrow = date.today() + timedelta(days=1)

    def test_booking_form_valid_data(self):
        from .forms import BookingForm

        form_data = {
            "table": self.table.id,
            "date": self.tomorrow.strftime("%Y-%m-%d"),
            "start_time": "12:00",
            "duration_hours": "2",
            "guests_count": "4",
            "special_requests": "Test request",
        }

        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_booking_form_guest_count_validation(self):
        from .forms import BookingForm

        small_table = Table.objects.create(number=6, capacity=2, is_active=True)

        form_data = {
            "table": small_table.id,
            "date": self.tomorrow.strftime("%Y-%m-%d"),
            "start_time": "12:00",
            "duration_hours": "2",
            "guests_count": "4",  # Больше вместимости
            "special_requests": "",
        }

        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("guests_count", form.errors)


class FeedbackFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

    def test_feedback_form_authenticated_user(self):
        from .forms import FeedbackForm

        self.client.login(email="test@example.com", password="testpass123")
        form = FeedbackForm(user=self.user)

        self.assertEqual(form.fields["email"].initial, "test@example.com")
        self.assertEqual(form.fields["name"].initial, "John Doe")

    def test_feedback_form_anonymous_user(self):
        from .forms import FeedbackForm

        form = FeedbackForm()
        self.assertIsNone(form.fields["email"].initial)
        self.assertIsNone(form.fields["name"].initial)


class BookingCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.table = Table.objects.create(number=10, capacity=4, is_active=True)
        self.booking = Booking.objects.create(
            user=self.user,
            table=self.table,
            date=date.today() + timedelta(days=2),
            start_time=time(15, 0, 0),
            end_time=time(17, 0, 0),
            guests_count=2,
        )
        self.client.login(email="test@example.com", password="testpass123")

    def test_booking_edit_view(self):
        response = self.client.get(reverse("booking_edit", args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)

    def test_booking_cancel_view(self):
        response = self.client.get(reverse("booking_cancel", args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)

    def test_booking_delete(self):
        response = self.client.post(reverse("booking_cancel", args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())
