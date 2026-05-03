from django.contrib import admin
from .models import DiscountCode, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    """Inline để quản lý items trong đơn hàng"""
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    autocomplete_fields = ['product']


class PaymentInline(admin.StackedInline):
    """Inline để quản lý thanh toán"""
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin cho Order"""
    list_display = ['order_number', 'customer', 'staff', 'final_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'customer__name', 'customer__phone']
    readonly_fields = ['order_number', 'order_date']
    autocomplete_fields = ['customer', 'staff']
    inlines = [OrderItemInline, PaymentInline]
    
    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_number', 'customer', 'staff', 'order_date', 'status')
        }),
        ('Thanh toán', {
            'fields': ('total_amount', 'discount', 'final_amount')
        }),
    )
    
    actions = ['mark_as_completed']
    
    def mark_as_completed(self, request, queryset):
        """Action đánh dấu đơn hàng hoàn thành"""
        count = queryset.update(status='completed')
        self.message_user(request, f'Đã đánh dấu {count} đơn hàng là hoàn thành')
    mark_as_completed.short_description = 'Đánh dấu hoàn thành'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin cho OrderItem"""
    list_display = ['order', 'product', 'size', 'quantity', 'price', 'subtotal']
    list_filter = ['size', 'order__order_date']
    search_fields = ['order__order_number', 'product__name']
    autocomplete_fields = ['order', 'product']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin cho Payment"""
    list_display = ['order', 'payment_method', 'amount', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['order__order_number']
    autocomplete_fields = ['order']


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'discount_percent',
        'min_order_amount',
        'max_discount_amount',
        'is_active',
        'valid_from',
        'valid_to',
    ]
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['code', 'name']
