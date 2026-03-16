from django.db import models


class Ingredient(models.Model):
    """
    Model nguyên liệu - quản lý kho nguyên liệu
    Ingredient model - inventory management
    """
    UNIT_CHOICES = [
        ('kg', 'Ki-lo-gam (kg)'),
        ('g', 'Gam (g)'),
        ('l', 'Lít (l)'),
        ('ml', 'Mili-lít (ml)'),
        ('pcs', 'Cái/Chiếc (pcs)'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Tên nguyên liệu')
    unit = models.CharField(
        max_length=20, 
        choices=UNIT_CHOICES,
        default='kg',
        verbose_name='Đơn vị'
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Số lượng hiện tại'
    )
    min_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Số lượng tối thiểu'
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Giá/đơn vị'
    )
    supplier = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Nhà cung cấp'
    )
    last_restock_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Ngày nhập gần nhất'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'ingredients'
        verbose_name = 'Nguyên liệu'
        verbose_name_plural = 'Nguyên liệu'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.quantity} {self.unit})'

    def is_low_stock(self):
        """Kiểm tra nguyên liệu sắp hết / Check if ingredient is low on stock"""
        return self.quantity <= self.min_quantity

    def deduct_stock(self, amount):
        """Trừ số lượng nguyên liệu / Deduct ingredient quantity"""
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
            return True
        return False

    def add_stock(self, amount):
        """Thêm số lượng nguyên liệu / Add ingredient quantity"""
        self.quantity += amount
        self.save()
