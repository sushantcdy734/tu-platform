from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.student_attendance, name='student_attendance'),
    path('sessions/', views.teacher_attendance, name='teacher_attendance'),
]