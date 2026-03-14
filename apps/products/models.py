from django.db import models


class Category(models.Model):
    """
    Model danh mục sản phẩm
    Category model for product classification
    """
    name = models.CharField(max_length=100, verbose_name='Tên danh mục')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'categories'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model sản phẩm với 3 size: S, M, L
    Product model with 3 sizes: Small, Medium, Large
    """
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='products',
        verbose_name='Danh mục'
    )
    name = models.CharField(max_length=100, verbose_name='Tên sản phẩm')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    price_small = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Giá size S'
    )
    price_medium = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Giá size M'
    )
    price_large = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Giá size L'
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True, 
        null=True,
        verbose_name='Hình ảnh'
    )
    is_available = models.BooleanField(default=True, verbose_name='Còn hàng')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'products'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def get_price(self, size):
        """Lấy giá theo size / Get price by size"""
        if size == 'N/A':
            # For products without sizes, return the medium price (or any available price)
            return self.price_medium or self.price_small or self.price_large
        elif size == 'S':
            return self.price_small
        elif size == 'M':
            return self.price_medium
        elif size == 'L':
            return self.price_large
        return self.price_medium


class Recipe(models.Model):
    """
    Model công thức pha chế - định nghĩa nguyên liệu cho từng size
    Recipe model - defines ingredients for each size
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Sản phẩm'
    )
    ingredient = models.ForeignKey(
        'ingredients.Ingredient',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Nguyên liệu'
    )
    quantity_small = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Khối lượng size S'
    )
    quantity_medium = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Khối lượng size M'
    )
    quantity_large = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Khối lượng size L'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'recipes'
        verbose_name = 'Công thức'
        verbose_name_plural = 'Công thức'
        unique_together = ['product', 'ingredient']

    def __str__(self):
        return f'{self.product.name} - {self.ingredient.name}'

    def get_quantity(self, size):
        """Lấy khối lượng nguyên liệu theo size / Get ingredient quantity by size"""
        if size == 'S':
            return self.quantity_small
        elif size == 'M':
            return self.quantity_medium
        elif size == 'L':
            return self.quantity_large
        return self.quantity_medium


class Customization(models.Model):
    """
    Model tùy chỉnh (đường, đá, topping, etc.)
    Customization model (sugar, ice, toppings, etc.)
    """
    CATEGORY_CHOICES = [
        ('sugar', 'Đường'),
        ('ice', 'Đá'),
        ('topping', 'Topping'),
        ('other', 'Khác'),
    ]

    name = models.CharField(max_length=100, verbose_name='Tên tùy chỉnh')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Giá'
    )
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Loại'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        db_table = 'customizations'
        verbose_name = 'Tùy chỉnh'
        verbose_name_plural = 'Tùy chỉnh'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} (+{self.price}đ)'
