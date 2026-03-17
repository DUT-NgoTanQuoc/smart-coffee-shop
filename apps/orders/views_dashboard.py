"""
Role-based Dashboard Views cho Coffee Shop
- Admin: Toàn bộ quản lý
- Cashier: Tạo đơn, xem danh sách đơn
- Barista: Queue system, chi tiết đơn, công thức, nguyên liệu
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from decimal import Decimal

from apps.orders.models import Order, OrderItem
from apps.ingredients.models import Ingredient
from apps.products.models import Product, Recipe
from apps.staff.models import Staff
from apps.core.decorators import admin_required, cashier_required, barista_required
from apps.core.utils import get_current_staff


@login_required
def admin_dashboard(request):
    """
    Admin Dashboard - Full Access
    - Staff management
    - Product management  
    - Ingredient management
    - Order management
    - Analytics
    """
    # Check if admin
    if not (request.user.is_superuser or (hasattr(request.user, 'staff') and request.user.staff.role == 'admin')):
        # Try to get_current_staff for checking
        try:
            staff = get_current_staff(request.user)
            if not (request.user.is_superuser or staff.role == 'admin'):
                messages.error(request, 'Chỉ Admin mới có quyền truy cập.')
                return redirect('dashboard')
        except:
            messages.error(request, 'Chỉ Admin mới có quyền truy cập.')
            return redirect('dashboard')
    
    # Get statistics
    today = timezone.now().date()
    
    context = {
        'total_orders': Order.objects.count(),
        'orders_today': Order.objects.filter(order_date__date=today).count(),
        'total_revenue': Order.objects.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0'),
        'revenue_today': Order.objects.filter(status='completed', order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0'),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'preparing_orders': Order.objects.filter(status='preparing').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'total_products': Product.objects.count(),
        'total_staff': Staff.objects.filter(is_active=True).count(),
        'low_stock_ingredients': Ingredient.objects.filter(quantity__lt=10),  # Assuming min_quantity or default 10
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def cashier_dashboard(request):
    """
    Cashier Dashboard - POS Interface
    - Left: Orders list
    - Middle: Products catalog
    - Right: Order details
    """
    # Check if cashier or admin
    if request.user.is_superuser:
        # Admin can also access cashier dashboard
        pass
    else:
        try:
            from apps.core.models import Account
            staff = Account.objects.get(username=request.user.username)
            if staff.role_id != 2:  # role_id 2 = cashier
                messages.error(request, 'Chỉ Cashier mới có quyền truy cập.')
                return redirect('dashboard')
        except Account.DoesNotExist:
            messages.error(request, 'Bạn không phải là Cashier.')
            return redirect('dashboard')
    
    # Get today's orders for left panel
    today = timezone.now().date()
    orders = Order.objects.filter(
        order_date__date=today
    ).select_related('customer', 'staff').order_by('-order_date')[:20]
    
    # Get all products for middle panel
    products = Product.objects.filter(is_available=True).order_by('category__name', 'name')[:30]
    
    context = {
        'orders': orders,
        'products': products,
        'status_choices': Order.STATUS_CHOICES,
        'today': today,
    }
    
    return render(request, 'dashboards/cashier_dashboard.html', context)


@login_required
def barista_dashboard(request):
    """
    Barista Dashboard - Queue System
    - View pending orders queue (chưa hoàn thành) on LEFT
    - View completed orders (hoàn thành) on RIGHT
    - Click order -> see items
    - Click item -> see recipe
    - Button "Hoàn thành" -> move to completed
    """
    from django.utils import timezone
    from datetime import date
    
    # Check if barista or admin
    if request.user.is_superuser:
        # Admin can view barista dashboard
        pass
    else:
        try:
            from apps.core.models import Account
            staff = Account.objects.get(username=request.user.username)
            if staff.role_id != 3:  # role_id 3 = barista
                messages.error(request, 'Chỉ Barista mới có quyền truy cập.')
                return redirect('dashboard')
        except Account.DoesNotExist:
            messages.error(request, 'Bạn không phải là Barista.')
            return redirect('dashboard')
    
    today = timezone.now().date()
    now = timezone.now()
    
    # LEFT: Đơn hàng chưa hoàn thành (pending + preparing) - TẤT CẢ, KHÔNG PHÂN BỠ NGÀY
    # Vì các đơn cũ vẫn cần được barista xử lý nếu chưa hoàn thành
    pending_orders = Order.objects.filter(
        status__in=['pending', 'preparing']
    ).select_related('customer', 'staff').prefetch_related(
        'items__product',
        'items__product__recipes__ingredient'
    ).order_by('order_date')
    
    print(f"[DEBUG] Barista dashboard: today={today}, pending={pending_orders.count()}")
    for o in pending_orders[:5]:
        print(f"  - Order {o.id}: status={o.status}, date={o.order_date}")
    
    # RIGHT: Đơn hàng đã hoàn thành trong 24 giờ gần nhất (từ bây giờ tính ngược)
    # Không lọc theo order_date vì các đơn cũ cũng có thể hoàn thành hôm nay
    from datetime import timedelta
    time_24h_ago = now - timedelta(hours=24)
    completed_orders = Order.objects.filter(
        status='completed',
        order_date__gte=time_24h_ago  # Lấy đơn từ 24h gần nhất
    ).select_related('customer', 'staff').order_by('-order_date')
    
    # Get low stock ingredients
    low_stock = Ingredient.objects.filter(
        quantity__lt=10  # TODO: Use min_quantity field
    )
    
    # Build ordersData JSON for JavaScript
    import json
    from decimal import Decimal
    
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super().default(obj)
    
    orders_data = {}
    for order in pending_orders:
        items_list = []
        for item in order.items.all():
            recipes_list = []
            for recipe in item.product.recipes.all():
                recipes_list.append({
                    'name': f'Công thức - {recipe.ingredient.name}',
                    'ingredient_name': recipe.ingredient.name,
                    'quantity_small': float(recipe.quantity_small) if hasattr(recipe.quantity_small, '__float__') else recipe.quantity_small,
                    'quantity_medium': float(recipe.quantity_medium) if hasattr(recipe.quantity_medium, '__float__') else recipe.quantity_medium,
                    'quantity_large': float(recipe.quantity_large) if hasattr(recipe.quantity_large, '__float__') else recipe.quantity_large,
                    'unit': recipe.ingredient.unit or 'pcs'
                })
            
            qty_for_size = {
                'S': item.product.price_small,
                'M': item.product.price_medium,
                'L': item.product.price_large,
            }.get(item.size, 1)
            
            items_list.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'size': item.size,
                'quantity': item.quantity,
                'recipes': recipes_list
            })
        
        orders_data[str(order.id)] = {
            'id': order.id,
            'number': order.order_number,
            'items': items_list
        }
    
    orders_data_json = json.dumps(orders_data, cls=DecimalEncoder)
    
    context = {
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'low_stock_ingredients': low_stock,
        'queue_count': pending_orders.count(),
        'orders_data_json': orders_data_json,
    }
    
    return render(request, 'dashboards/barista_dashboard.html', context)


@login_required
def order_queue(request):
    """
    Barista Queue API - Get queue data for updating status
    """
    try:
        staff = get_current_staff(request.user)
        if not staff or staff.role not in ['barista', 'admin']:
            return render(request, 'error.html', {'message': 'Unauthorized'}, status=403)
    except:
        if not request.user.is_superuser:
            return render(request, 'error.html', {'message': 'Unauthorized'}, status=403)
    
    orders = Order.objects.filter(
        status__in=['pending', 'preparing']
    ).values('id', 'id__customer__name', 'status', 'created_at').order_by('created_at')
    
    return render(request, 'orders/queue_list.html', {'orders': orders})


@login_required
def order_detail_barista(request, order_id):
    """
    Barista View - Order detail with items and recipes
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Verify barista can view this
    if not (request.user.is_superuser):
        try:
            staff = get_current_staff(request.user)
            if not staff or staff.role not in ['barista', 'admin']:
                messages.error(request, 'Bạn không có quyền xem đơn này.')
                return redirect('barista-dashboard')
        except:
            messages.error(request, 'Bạn không có quyền xem đơn này.')
            return redirect('barista-dashboard')
    
    # Get order items with recipes
    items = order.items.all().prefetch_related('product__recipes__ingredient')
    
    # Get ingredients used in this order
    ingredients_used = {}
    for item in items:
        for recipe in item.product.recipes.all():
            ing_id = recipe.ingredient.id
            quantity = recipe.quantity * item.quantity
            if ing_id in ingredients_used:
                ingredients_used[ing_id]['quantity'] += quantity
            else:
                ingredients_used[ing_id] = {
                    'ingredient': recipe.ingredient,
                    'quantity': quantity,
                    'unit': recipe.ingredient.unit,
                }
    
    context = {
        'order': order,
        'items': items,
        'ingredients_used': ingredients_used.values(),
    }
    
    return render(request, 'dashboards/barista_order_detail.html', context)


@login_required
def recipe_view(request, product_id):
    """
    Barista View - Product recipe (ingredients and quantities)
    """
    product = get_object_or_404(Product, id=product_id)
    recipes = product.recipes.all().select_related('ingredient')
    
    context = {
        'product': product,
        'recipes': recipes,
    }
    
    return render(request, 'dashboards/recipe_detail.html', context)


@login_required
def ingredient_tracking(request):
    """
    Ingredient Tracking Page - For all staff
    Shows all ingredients with quantities and alerts
    """
    ingredients = Ingredient.objects.all().order_by('name')
    
    # Separate low stock
    low_stock = [ing for ing in ingredients if ing.quantity < (ing.min_quantity if hasattr(ing, 'min_quantity') else 10)]
    
    context = {
        'ingredients': ingredients,
        'low_stock_count': len(low_stock),
        'low_stock': low_stock,
    }
    
    return render(request, 'dashboards/ingredient_tracking.html', context)
