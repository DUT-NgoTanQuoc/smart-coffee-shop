from django.urls import path
from . import views

urlpatterns = [
    path('revenue-forecast/', views.revenue_forecast, name='revenue_forecast'),
    path('stock-prediction/', views.stock_prediction, name='stock_prediction'),
    path('trends/', views.trends, name='trends'),
]
