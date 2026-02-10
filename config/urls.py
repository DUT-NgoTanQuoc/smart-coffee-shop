"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.analytics import views as analytics_views

# Tùy chỉnh admin site
admin.site.site_header = 'Smart Coffee Shop - Quản trị'
admin.site.site_title = 'Smart Coffee Shop Admin'
admin.site.index_title = 'Bảng điều khiển'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('', analytics_views.dashboard, name='dashboard'),
    
    # Analytics
    path('analytics/', include('apps.analytics.urls')),
    
    # Orders (POS)
    path('orders/', include('apps.orders.urls')),
    
    # Products
    path('products/', include('apps.products.urls')),
    
    # Ingredients
    path('ingredients/', include('apps.ingredients.urls')),
    
    # Customers
    path('customers/', include('apps.customers.urls')),
    
    # Staff
    path('staff/', include('apps.staff.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
