from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.page_detail, {"page_type": "about"}, name="about"),
    path("gallery/", views.page_detail, {"page_type": "gallery"}, name="gallery"),
    path("menu/", views.page_detail, {"page_type": "menu"}, name="menu"),
    path("team/", views.page_detail, {"page_type": "team"}, name="team"),
    path("feedback/", views.feedback, name="feedback"),
    path("booking/create/", views.booking_create, name="booking_create"),
    path("booking/list/", views.booking_list, name="booking_list"),
    path(
        "booking/cancel/<int:booking_id>/", views.booking_cancel, name="booking_cancel"
    ),
    path(
        "tables/<int:table_id>/capacity/",
        views.get_table_capacity,
        name="table_capacity",
    ),
]
