from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('create/', views.staff_create, name='staff_create'),
    path('<int:staff_id>/edit/', views.staff_update, name='staff_update'),
    path('<int:staff_id>/delete/', views.staff_delete, name='staff_delete'),
    path('<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('attendance/', views.attendance_list, name='attendance_list'),
]
