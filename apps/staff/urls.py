from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('create/', views.staff_create, name='staff_create'),
    path('payroll/', views.staff_payroll_summary, name='staff_payroll_summary'),
    path('assignments/<int:assignment_id>/delete/', views.shift_assignment_delete, name='shift_assignment_delete'),
    path('schedule/', views.schedule_calendar, name='schedule_calendar'),
    path('schedule/api/events/', views.schedule_api_events, name='schedule_api_events'),
    path('schedule/api/create/', views.schedule_api_create, name='schedule_api_create'),
    path('schedule/api/<int:assignment_id>/update/', views.schedule_api_update, name='schedule_api_update'),
    path('schedule/api/<int:assignment_id>/delete/', views.schedule_api_delete, name='schedule_api_delete'),
    # Backward-compatible legacy routes
    path('schedule/events/', views.schedule_events, name='schedule_events'),
    path('schedule/events/<int:assignment_id>/delete/', views.schedule_event_delete, name='schedule_event_delete'),
    path('<int:staff_id>/edit/', views.staff_update, name='staff_update'),
    path('<int:staff_id>/delete/', views.staff_delete, name='staff_delete'),
    path('<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('attendance/', views.attendance_list, name='attendance_list'),
]
