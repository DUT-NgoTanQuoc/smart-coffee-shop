"""
Signals for order lifecycle.

Important behavior:
- Reward points, ingredient deduction, and daily stats are applied only once,
  when an order transitions to `completed`.
"""

from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Order
from apps.analytics.models import DailyStat
from apps.ingredients.models import Ingredient
from apps.products.models import Recipe


@receiver(pre_save, sender=Order)
def _store_previous_status(sender, instance, **kwargs):
    """Attach previous status to instance before save for transition checks."""
    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = (
        Order.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    )


def _became_completed(instance, created):
    """Return True only when status changed into completed."""
    if instance.status != 'completed':
        return False

    if created:
        return True

    previous_status = getattr(instance, '_previous_status', None)
    return previous_status != 'completed'


@receiver(post_save, sender=Order)
def _apply_completion_side_effects(sender, instance, created, **kwargs):
    """Apply side effects exactly once when order moves to completed."""
    if not _became_completed(instance, created):
        return

    with transaction.atomic():
        if instance.customer:
            points = instance.calculate_points()
            instance.customer.add_points(points)
            Order.objects.filter(pk=instance.pk).update(points_earned=points)

        order_items = instance.items.select_related('product').prefetch_related('product__recipes__ingredient')
        for order_item in order_items:
            if not order_item.product:
                continue
            recipes = Recipe.objects.filter(product=order_item.product).select_related('ingredient')
            for recipe in recipes:
                deduction = recipe.get_quantity(order_item.size) * order_item.quantity
                Ingredient.objects.filter(pk=recipe.ingredient_id).update(
                    quantity=F('quantity') - deduction
                )

        order_dt = instance.order_date
        if order_dt and timezone.is_naive(order_dt):
            order_dt = timezone.make_aware(order_dt, timezone.get_current_timezone())
        stat_date = timezone.localdate(order_dt) if order_dt else timezone.localdate()
        daily_stat, _ = DailyStat.objects.get_or_create(
            stat_date=stat_date,
            defaults={
                'total_revenue': 0,
                'total_orders': 0,
                'total_customers': 0,
            },
        )

        update_fields = {
            'total_revenue': F('total_revenue') + instance.final_amount,
            'total_orders': F('total_orders') + 1,
        }
        if instance.customer_id:
            update_fields['total_customers'] = F('total_customers') + 1

        DailyStat.objects.filter(pk=daily_stat.pk).update(**update_fields)
