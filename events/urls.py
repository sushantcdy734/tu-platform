from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/register/', views.event_register, name='event_register'),
    path('<int:pk>/unregister/', views.event_unregister, name='event_unregister'),
    path('<int:pk>/attendees/', views.event_attendees, name='event_attendees'),
]