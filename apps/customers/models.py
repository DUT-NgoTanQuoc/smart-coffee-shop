from django.db import models


class Customer(models.Model):
    """
    Model khách hàng với hệ thống tích điểm và cấp bậc
    Customer model with points and tier system
    """
    TIER_CHOICES = [
        ('Đồng', 'Đồng'),
        ('Bạc', 'Bạc'),
        ('Vàng', 'Vàng'),
        ('Kim cương', 'Kim cương'),
    ]

    name = models.CharField(max_length=100, verbose_name='Tên khách hàng')
    phone = models.CharField(max_length=20, unique=True, verbose_name='Số điện thoại')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    points = models.IntegerField(default=0, verbose_name='Điểm tích lũy')
    tier = models.CharField(
        max_length=20, 
        choices=TIER_CHOICES,
        default='Đồng',
        verbose_name='Hạng thành viên'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'customers'
        verbose_name = 'Khách hàng'
        verbose_name_plural = 'Khách hàng'
        ordering = ['-points']

    def __str__(self):
        return f'{self.name} ({self.phone})'

    def add_points(self, points):
        """Thêm điểm và cập nhật hạng / Add points and update tier"""
        self.points += points
        self.update_tier()
        self.save()

    def update_tier(self):
        """
        Cập nhật hạng thành viên dựa trên điểm
        Update tier based on points
        Đồng: 0-499, Bạc: 500-1999, Vàng: 2000-4999, Kim cương: 5000+
        """
        if self.points >= 5000:
            self.tier = 'Kim cương'
        elif self.points >= 2000:
            self.tier = 'Vàng'
        elif self.points >= 500:
            self.tier = 'Bạc'
        else:
            self.tier = 'Đồng'

    def get_discount_percentage(self):
        """Lấy % giảm giá theo hạng / Get discount percentage by tier"""
        discounts = {
            'Đồng': 0,
            'Bạc': 5,
            'Vàng': 10,
            'Kim cương': 15,
        }
        return discounts.get(self.tier, 0)


class FavoriteDrink(models.Model):
    """
    Model đồ uống yêu thích của khách hàng
    Customer's favorite drink model
    """
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='favorite_drinks',
        verbose_name='Khách hàng'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Sản phẩm'
    )
    size = models.CharField(
        max_length=10, 
        choices=SIZE_CHOICES,
        verbose_name='Size'
    )
    customizations = models.JSONField(
        blank=True, 
        null=True,
        verbose_name='Tùy chỉnh (JSON)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'favorite_drinks'
        verbose_name = 'Đồ uống yêu thích'
        verbose_name_plural = 'Đồ uống yêu thích'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer.name} - {self.product.name} ({self.size})'
