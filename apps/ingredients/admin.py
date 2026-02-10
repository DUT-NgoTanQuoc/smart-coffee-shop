from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin cho Ingredient"""
    list_display = ['name', 'unit', 'quantity', 'min_quantity', 'price_per_unit', 'supplier', 'last_restock_date', 'is_low_stock']
    list_filter = ['last_restock_date', 'created_at']
    search_fields = ['name', 'supplier']
    list_editable = ['quantity', 'min_quantity']
    
    fieldsets = (
        ('Thông tin nguyên liệu', {
            'fields': ('name', 'unit', 'supplier')
        }),
        ('Quản lý kho', {
            'fields': ('quantity', 'min_quantity', 'price_per_unit', 'last_restock_date')
        }),
    )
    
    def is_low_stock(self, obj):
        """Hiển thị trạng thái sắp hết hàng"""
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Sắp hết'
    
    actions = ['restock_ingredients']
    
    def restock_ingredients(self, request, queryset):
        """Action để nhập thêm hàng"""
        for ingredient in queryset:
            # Thêm 100 đơn vị mẫu
            ingredient.add_stock(100)
        self.message_user(request, f'Đã nhập thêm hàng cho {queryset.count()} nguyên liệu')
    restock_ingredients.short_description = 'Nhập thêm hàng (mẫu)'
