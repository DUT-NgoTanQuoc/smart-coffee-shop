"""
Django Signals cho hệ thống đơn hàng
Thay thế PostgreSQL triggers bằng Django signals

Chức năng:
1. Tự động cập nhật điểm khách hàng khi đơn hàng hoàn thành
2. Tự động nâng cấp hạng thành viên dựa trên điểm
3. Tự động trừ nguyên liệu khi đơn hàng hoàn thành
4. Tự động tạo order_number
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, OrderItem
from apps.customers.models import Customer
from apps.products.models import Recipe
from apps.ingredients.models import Ingredient


@receiver(post_save, sender=Order)
def update_customer_points_and_tier(sender, instance, created, **kwargs):
    """
    Signal: Cập nhật điểm và hạng khách hàng khi đơn hàng hoàn thành
    Trigger when: Order status changes to 'completed'
    """
    if instance.status == 'completed' and instance.customer:
        # Tính điểm từ đơn hàng (1 điểm = 10,000đ)
        points = instance.calculate_points()
        
        # Thêm điểm vào khách hàng (tự động cập nhật tier trong method)
        instance.customer.add_points(points)


@receiver(post_save, sender=Order)
def deduct_ingredients_on_complete(sender, instance, created, **kwargs):
    """
    Signal: Trừ nguyên liệu khi đơn hàng hoàn thành
    Trigger when: Order status changes to 'completed'
    """
    if instance.status == 'completed':
        # Lấy tất cả items trong đơn hàng
        for order_item in instance.items.all():
            product = order_item.product
            size = order_item.size
            quantity = order_item.quantity
            
            # Lấy công thức của sản phẩm
            recipes = Recipe.objects.filter(product=product)
            
            for recipe in recipes:
                # Tính lượng nguyên liệu cần trừ
                ingredient_quantity = recipe.get_quantity(size) * quantity
                
                # Trừ nguyên liệu
                ingredient = recipe.ingredient
                ingredient.deduct_stock(ingredient_quantity)


@receiver(post_save, sender=Order)
def update_daily_stats(sender, instance, created, **kwargs):
    """
    Signal: Cập nhật thống kê hàng ngày khi đơn hàng hoàn thành
    Trigger when: Order status changes to 'completed'
    """
    if instance.status == 'completed':
        from apps.analytics.models import DailyStat
        from django.utils import timezone
        
        today = timezone.now().date()
        
        # Lấy hoặc tạo daily stat
        daily_stat, created_stat = DailyStat.objects.get_or_create(
            stat_date=today,
            defaults={
                'total_revenue': 0,
                'total_orders': 0,
                'total_customers': 0,
            }
        )
        
        # Cập nhật thống kê
        daily_stat.total_revenue += instance.final_amount
        daily_stat.total_orders += 1
        if instance.customer:
            daily_stat.total_customers += 1
        daily_stat.save()
