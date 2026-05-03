from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Order(models.Model):
    """
    Model đơn hàng với tự động tạo số đơn
    Order model with auto order number generation
    """
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('preparing', 'Đang chế biến'),
        ('completed', 'Hoàn thành'),
    ]

    order_number = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        verbose_name='Số đơn hàng'
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Khách hàng'
    )
    staff = models.ForeignKey(
        'staff.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Nhân viên'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Tổng tiền'
    )
    discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Giảm giá'
    )
    final_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Thành tiền'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    points_earned = models.IntegerField(default=0, verbose_name='Điểm tích lũy')
    points_used = models.IntegerField(default=0, verbose_name='Điểm đã dùng')
    order_date = models.DateTimeField(default=timezone.now, verbose_name='Ngày đặt')

    class Meta:
        db_table = 'orders'
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-order_date']

    def __str__(self):
        return f'{self.order_number} - {self.final_amount}đ'

    def save(self, *args, **kwargs):
        """Tự động tạo order_number / Auto-generate order_number"""
        if not self.order_number:
            today = timezone.localtime(timezone.now())
            prefix = f'ORD{today.strftime("%Y%m%d")}'
            
            # Lấy đơn hàng cuối cùng trong ngày
            last_order = Order.objects.filter(
                order_number__startswith=prefix
            ).order_by('-order_number').first()
            
            if last_order:
                # Lấy số thứ tự và tăng lên 1
                last_number = int(last_order.order_number[-3:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_number = f'{prefix}{new_number:03d}'
        
        super().save(*args, **kwargs)

    def calculate_points(self):
        """Tính điểm thưởng (1 điểm = 10,000đ) / Calculate reward points"""
        return int(self.final_amount / 10000)


class OrderItem(models.Model):
    """
    Model chi tiết đơn hàng
    Order item model
    """
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('N/A', 'Không size'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Đơn hàng'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='Sản phẩm'
    )
    size = models.CharField(
        max_length=10, 
        choices=SIZE_CHOICES,
        verbose_name='Size'
    )
    quantity = models.IntegerField(verbose_name='Số lượng')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Đơn giá'
    )
    customizations = models.JSONField(
        blank=True, 
        null=True,
        verbose_name='Tùy chỉnh (JSON)'
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Thành tiền'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        return f'{self.product.name} ({self.size}) x{self.quantity}'


class Payment(models.Model):
    """
    Model thanh toán
    Payment model
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tiền mặt'),
        ('card', 'Thẻ'),
        ('momo', 'MoMo'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Đơn hàng'
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Phương thức'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Số tiền'
    )
    payment_date = models.DateTimeField(default=timezone.now, verbose_name='Ngày thanh toán')

    class Meta:
        db_table = 'payments'
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Thanh toán'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.order.order_number} - {self.get_payment_method_display()}'


class DiscountCode(models.Model):
    """
    Discount code model used by POS.
    """

    code = models.CharField(max_length=50, unique=True, verbose_name='Mã giảm giá')
    name = models.CharField(max_length=120, blank=True, null=True, verbose_name='Tên chương trình')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Phần trăm giảm',
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Giá trị đơn tối thiểu',
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Giảm tối đa',
    )
    valid_from = models.DateTimeField(blank=True, null=True, verbose_name='Hiệu lực từ')
    valid_to = models.DateTimeField(blank=True, null=True, verbose_name='Hiệu lực đến')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'discount_codes'
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Mã giảm giá'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.discount_percent}%)'

    def clean(self):
        if self.discount_percent <= 0 or self.discount_percent > 100:
            raise ValidationError('Phần trăm giảm phải > 0 và <= 100')
        if self.max_discount_amount is not None and self.max_discount_amount < 0:
            raise ValidationError('Giảm tối đa không được âm')
        if self.min_order_amount < 0:
            raise ValidationError('Giá trị đơn tối thiểu không được âm')

    def is_currently_valid(self):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True

    def calculate_discount(self, total_amount):
        total = Decimal(str(total_amount or 0))
        if total < self.min_order_amount:
            return Decimal('0')

        discount = (total * self.discount_percent) / Decimal('100')
        if self.max_discount_amount is not None:
            discount = min(discount, self.max_discount_amount)
        return max(Decimal('0'), discount.quantize(Decimal('0.01')))
