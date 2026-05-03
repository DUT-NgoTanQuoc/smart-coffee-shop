from django.urls import path
from . import views
from .views_dashboard import (
    admin_dashboard, cashier_dashboard, barista_dashboard,
    order_detail_barista, recipe_view, ingredient_tracking, order_queue
)

urlpatterns = [
    # Existing order views
    path('create/', views.create_order, name='create_order'),
    path('validate-discount/', views.validate_discount_code, name='validate_discount_code'),
    path('list/', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('search-customer/', views.search_customer, name='search_customer'),
    
    # API endpoints
    path('api/<int:order_id>/status/', views.update_order_status, name='api-update-status'),
    
    # Dashboard views
    path('dashboard/admin/', admin_dashboard, name='admin-dashboard'),
    path('dashboard/cashier/', cashier_dashboard, name='cashier-dashboard'),
    path('dashboard/barista/', barista_dashboard, name='barista-dashboard'),
    path('dashboard/barista/queue/', order_queue, name='barista-queue'),
    path('dashboard/barista/order/<int:order_id>/', order_detail_barista, name='barista-order-detail'),
    path('dashboard/recipe/<int:product_id>/', recipe_view, name='recipe-view'),
    path('dashboard/ingredients/', ingredient_tracking, name='ingredient-tracking'),
]
