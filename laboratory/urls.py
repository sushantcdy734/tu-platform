from django.urls import path
from . import views

urlpatterns = [
    path('', views.lab_list, name='lab_list'),
    path('my-bookings/', views.my_bookings, name='my_lab_bookings'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('<int:pk>/', views.lab_detail, name='lab_detail'),
    path('<int:pk>/book/', views.lab_book, name='lab_book'),
    path('<int:pk>/bookings/<int:booking_id>/review/', views.booking_review, name='booking_review'),
    path('equipment/<int:equipment_id>/maintenance/', views.report_maintenance, name='report_maintenance'),
]