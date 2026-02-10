from django.urls import path
from . import views

urlpatterns = [
    path('', views.ingredient_list, name='ingredient_list'),
    path('create/', views.ingredient_create, name='ingredient_create'),
    path('<int:ingredient_id>/update/', views.ingredient_update, name='ingredient_update'),
    path('<int:ingredient_id>/restock/', views.ingredient_restock, name='ingredient_restock'),
]
