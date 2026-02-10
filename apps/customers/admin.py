from django.contrib import admin
from .models import Customer, FavoriteDrink


class FavoriteDrinkInline(admin.TabularInline):
    """Inline để quản lý đồ uống yêu thích"""
    model = FavoriteDrink
    extra = 0
    autocomplete_fields = ['product']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin cho Customer"""
    list_display = ['name', 'phone', 'email', 'points', 'tier', 'created_at']
    list_filter = ['tier', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['points', 'tier']
    inlines = [FavoriteDrinkInline]
    
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Tích điểm', {
            'fields': ('points', 'tier'),
            'description': 'Điểm và hạng được cập nhật tự động'
        }),
    )


@admin.register(FavoriteDrink)
class FavoriteDrinkAdmin(admin.ModelAdmin):
    """Admin cho FavoriteDrink"""
    list_display = ['customer', 'product', 'size', 'created_at']
    list_filter = ['size', 'created_at']
    search_fields = ['customer__name', 'product__name']
    autocomplete_fields = ['customer', 'product']
