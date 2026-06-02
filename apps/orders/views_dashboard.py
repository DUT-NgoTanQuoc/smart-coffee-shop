"""
Role-based dashboard views for the coffee shop.
"""

import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.models import Account
from apps.core.utils import get_current_staff
from apps.ingredients.models import Ingredient
from apps.orders.models import Order
from apps.products.models import Product
from apps.staff.models import Staff

ROLE_ID_TO_NAME = {
    1: 'admin',
    2: 'cashier',
    3: 'barista',
    4: 'parttime',
}


def _resolve_user_role(user):
    """Resolve current role from custom auth, staff, or accounts table."""
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser:
        return 'admin'

    user_role = getattr(user, 'role', None)
    if user_role:
        return user_role

    try:
        staff = get_current_staff(user)
        if staff:
            return staff.role
    except Exception:
        pass

    try:
        account = Account.objects.filter(username=user.username).only('role_id').first()
        if account and account.role_id:
            return ROLE_ID_TO_NAME.get(account.role_id)
    except Exception:
        pass

    return None


def _has_any_role(user, *allowed_roles):
    if user and user.is_authenticated and user.is_superuser:
        return True
    return _resolve_user_role(user) in set(allowed_roles)


@login_required
def admin_dashboard(request):
    """Legacy admin dashboard path -> redirect to the unified dashboard."""
    if not _has_any_role(request.user, 'admin', 'manager'):
        messages.error(request, 'Chi Admin/Manager moi co quyen truy cap.')
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def cashier_dashboard(request):
    """Cashier dashboard."""
    if not _has_any_role(request.user, 'cashier', 'admin', 'manager'):
        messages.error(request, 'Chi Cashier/Admin/Manager moi co quyen truy cap.')
        return redirect('dashboard')

    today = timezone.now().date()
    orders = (
        Order.objects.filter(order_date__date=today)
        .select_related('customer', 'staff')
        .order_by('-order_date')[:20]
    )
    products = Product.objects.filter(is_available=True).order_by('category__name', 'name')[:30]

    return render(
        request,
        'dashboards/cashier_dashboard.html',
        {
            'orders': orders,
            'products': products,
            'status_choices': Order.STATUS_CHOICES,
            'today': today,
        },
    )


@login_required
def barista_dashboard(request):
    """Barista queue dashboard."""
    if not _has_any_role(request.user, 'barista', 'admin', 'manager'):
        messages.error(request, 'Chi Barista/Admin/Manager moi co quyen truy cap.')
        return redirect('dashboard')

    now = timezone.now()

    pending_orders = (
        Order.objects.filter(status__in=['pending', 'preparing'])
        .select_related('customer', 'staff')
        .prefetch_related('items__product', 'items__product__recipes__ingredient')
        .order_by('order_date')
    )

    completed_orders = (
        Order.objects.filter(status='completed', order_date__date=now.date())
        .select_related('customer', 'staff')
        .order_by('-order_date')
    )

    low_stock = Ingredient.objects.filter(quantity__lte=F('min_quantity')).order_by('name')

    orders_data = {}
    for order in pending_orders:
        items_list = []
        for item in order.items.all():
            recipes_list = []
            if item.product:
                for recipe in item.product.recipes.all():
                    recipes_list.append(
                        {
                            'name': f'Cong thuc - {recipe.ingredient.name}',
                            'ingredient_name': recipe.ingredient.name,
                            'quantity': float(recipe.get_quantity(item.size)),
                            'unit': recipe.ingredient.unit or 'pcs',
                        }
                    )

            items_list.append(
                {
                    'id': item.id,
                    'product_id': item.product.id if item.product else None,
                    'name': item.product.name if item.product else 'San pham da xoa',
                    'size': item.size,
                    'quantity': item.quantity,
                    'recipes': recipes_list,
                }
            )

        orders_data[str(order.id)] = {
            'id': order.id,
            'number': order.order_number,
            'items': items_list,
        }

    notification_count = pending_orders.count()

    return render(
        request,
        'dashboards/barista_dashboard.html',
        {
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'low_stock_ingredients': low_stock,
            'queue_count': pending_orders.count(),
            'notification_count': notification_count,
            'orders_data_json': json.dumps(orders_data),
        },
    )


@login_required
def barista_dashboard_data(request):
    """Realtime payload for the barista dashboard."""
    if not _has_any_role(request.user, 'barista', 'admin', 'manager'):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    now = timezone.now()
    pending_orders = (
        Order.objects.filter(status__in=['pending', 'preparing'])
        .select_related('customer', 'staff')
        .prefetch_related('items__product', 'items__product__recipes__ingredient')
        .order_by('order_date')
    )

    completed_orders = (
        Order.objects.filter(status='completed', order_date__date=now.date())
        .select_related('customer', 'staff')
        .order_by('-order_date')
    )

    orders_data = {}
    for order in pending_orders:
        items_list = []
        for item in order.items.all():
            recipes_list = []
            if item.product:
                for recipe in item.product.recipes.all():
                    recipes_list.append(
                        {
                            'ingredient_name': recipe.ingredient.name,
                            'quantity': float(recipe.get_quantity(item.size)),
                            'unit': recipe.ingredient.unit or 'pcs',
                        }
                    )

            items_list.append(
                {
                    'id': item.id,
                    'product_id': item.product.id if item.product else None,
                    'name': item.product.name if item.product else 'San pham da xoa',
                    'size': item.size,
                    'quantity': item.quantity,
                    'recipes': recipes_list,
                }
            )

        orders_data[str(order.id)] = {
            'id': order.id,
            'number': order.order_number,
            'customer_name': order.customer.name if order.customer else '',
            'order_time': order.order_date.strftime('%H:%M:%S') if order.order_date else '',
            'items': items_list,
        }

    completed_list = [
        {
            'id': order.id,
            'order_number': order.order_number,
            'order_time': order.order_date.strftime('%H:%M:%S') if order.order_date else '',
            'customer_name': order.customer.name if order.customer else '',
        }
        for order in completed_orders
    ]

    return JsonResponse(
        {
            'success': True,
            'pending_count': pending_orders.count(),
            'completed_count': completed_orders.count(),
            'pending_orders': orders_data,
            'completed_orders': completed_list,
        }
    )


@login_required
def order_queue(request):
    """Queue API for barista screen."""
    if not _has_any_role(request.user, 'barista', 'admin', 'manager'):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    orders = (
        Order.objects.filter(status__in=['pending', 'preparing'])
        .select_related('customer')
        .order_by('order_date')
    )

    serialized_orders = [
        {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'customer_name': order.customer.name if order.customer else None,
        }
        for order in orders
    ]

    return JsonResponse({'success': True, 'orders': serialized_orders})


@login_required
def order_detail_barista(request, order_id):
    """Barista order detail with recipe and required ingredients."""
    if not _has_any_role(request.user, 'barista', 'admin', 'manager'):
        messages.error(request, 'Ban khong co quyen xem don nay.')
        return redirect('barista-dashboard')

    order = get_object_or_404(Order, id=order_id)

    items = order.items.select_related('product').prefetch_related('product__recipes__ingredient')

    ingredients_used = {}
    for item in items:
        if not item.product:
            continue
        for recipe in item.product.recipes.all():
            ing_id = recipe.ingredient.id
            quantity = recipe.get_quantity(item.size) * item.quantity
            if ing_id in ingredients_used:
                ingredients_used[ing_id]['quantity'] += quantity
            else:
                ingredients_used[ing_id] = {
                    'ingredient': recipe.ingredient,
                    'quantity': quantity,
                    'unit': recipe.ingredient.unit,
                }

    return render(
        request,
        'dashboards/barista_order_detail.html',
        {
            'order': order,
            'items': items,
            'ingredients_used': ingredients_used.values(),
        },
    )


@login_required
def recipe_view(request, product_id):
    """Barista recipe detail for a product."""
    product = get_object_or_404(Product, id=product_id)
    recipes = product.recipes.all().select_related('ingredient')

    return render(
        request,
        'dashboards/recipe_detail.html',
        {
            'product': product,
            'recipes': recipes,
        },
    )


@login_required
def ingredient_tracking(request):
    """Ingredient overview page for staff."""
    ingredients = Ingredient.objects.all().order_by('name')
    low_stock = [ing for ing in ingredients if ing.quantity <= ing.min_quantity]

    return render(
        request,
        'dashboards/ingredient_tracking.html',
        {
            'ingredients': ingredients,
            'low_stock_count': len(low_stock),
            'low_stock': low_stock,
        },
    )
