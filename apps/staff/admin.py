from django.contrib import admin
from .models import Staff, WorkLog


class WorkLogInline(admin.TabularInline):
    """Inline để quản lý chấm công"""
    model = WorkLog
    extra = 0
    readonly_fields = ['hours_worked']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Admin cho Staff"""
    list_display = ['name', 'phone', 'email', 'role', 'salary', 'hire_date', 'is_active']
    list_filter = ['role', 'is_active', 'hire_date']
    search_fields = ['name', 'phone', 'email']
    list_editable = ['is_active']
    inlines = [WorkLogInline]
    
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Thông tin công việc', {
            'fields': ('role', 'salary', 'hire_date', 'is_active')
        }),
    )


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    """Admin cho WorkLog"""
    list_display = ['staff', 'work_date', 'check_in', 'check_out', 'hours_worked']
    list_filter = ['work_date', 'staff']
    search_fields = ['staff__name']
    autocomplete_fields = ['staff']
    readonly_fields = ['hours_worked']
    
    def save_model(self, request, obj, form, change):
        """Tự động tính giờ làm khi lưu"""
        super().save_model(request, obj, form, change)
        obj.calculate_hours()
