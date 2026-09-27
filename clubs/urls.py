from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('<int:pk>/', views.club_detail, name='club_detail'),
    path('<int:pk>/join/', views.club_join, name='club_join'),
    path('<int:pk>/leave/', views.club_leave, name='club_leave'),
    path('<int:pk>/members/<int:membership_id>/review/', views.membership_review, name='membership_review'),
    path('<int:pk>/announce/', views.club_announce, name='club_announce'),
]