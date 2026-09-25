from django.urls import path
from . import views

urlpatterns = [
    path('exams/', views.teacher_exams, name='teacher_exams'),
    path('exams/<int:exam_id>/marks/', views.exam_marks, name='exam_marks'),
    path('results/', views.student_results, name='student_results'),
]