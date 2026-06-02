from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('discount-codes/', views.discount_code_manager, name='discount_code_manager'),
    path('discount-codes/create/', views.discount_code_create, name='discount_code_create'),
    path('discount-codes/<int:code_id>/update/', views.discount_code_update, name='discount_code_update'),
    path('discount-codes/<int:code_id>/delete/', views.discount_code_delete, name='discount_code_delete'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('create/', views.product_create, name='product_create'),
    path('<int:product_id>/update/', views.product_update, name='product_update'),
    path('<int:product_id>/delete/', views.product_delete, name='product_delete'),
]
