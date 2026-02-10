from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('attendance/', views.attendance_list, name='attendance_list'),
]
