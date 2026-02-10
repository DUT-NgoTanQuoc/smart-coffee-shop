from django.contrib import admin
from .models import DailyStat


@admin.register(DailyStat)
class DailyStatAdmin(admin.ModelAdmin):
    """Admin cho DailyStat"""
    list_display = ['stat_date', 'total_revenue', 'total_orders', 'total_customers']
    list_filter = ['stat_date']
    search_fields = ['stat_date']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        """Không cho phép thêm thủ công"""
        return False
