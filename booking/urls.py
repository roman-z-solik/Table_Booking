from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback, name='feedback'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('booking/list/', views.booking_list, name='booking_list'),
    path('booking/cancel/<int:booking_id>/', views.booking_cancel, name='booking_cancel'),
]
