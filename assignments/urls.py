from django.urls import path
from . import views

urlpatterns = [
    path('teacher/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('', views.student_assignments, name='student_assignments'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
]