from django.contrib import admin
from .models import Category, Product, Recipe, Customization


class RecipeInline(admin.TabularInline):
    """Inline để quản lý công thức trong trang sản phẩm"""
    model = Recipe
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin cho Category"""
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin cho Product với inline recipes"""
    list_display = ['name', 'category', 'price_small', 'price_medium', 'price_large', 'is_available', 'created_at']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available']
    autocomplete_fields = ['category']
    inlines = [RecipeInline]
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'category', 'description', 'image', 'is_available')
        }),
        ('Giá theo size', {
            'fields': ('price_small', 'price_medium', 'price_large')
        }),
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin cho Recipe"""
    list_display = ['product', 'ingredient', 'quantity_small', 'quantity_medium', 'quantity_large']
    list_filter = ['product__category']
    search_fields = ['product__name', 'ingredient__name']
    autocomplete_fields = ['product', 'ingredient']


@admin.register(Customization)
class CustomizationAdmin(admin.ModelAdmin):
    """Admin cho Customization"""
    list_display = ['name', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name']
    list_editable = ['price']
