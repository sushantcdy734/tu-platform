from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('my/', views.my_books, name='my_books'),
    path('overdue/', views.overdue_list, name='overdue_list'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/issue/', views.issue_book, name='issue_book'),
    path('<int:pk>/return/<int:issue_id>/', views.return_book, name='return_book'),
]